import os
import string
import random
from datetime import datetime
from flask import Flask, request, redirect, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from user_agents import parse
import requests

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database Models
class ShortenedURL(db.Model):
    __tablename__ = 'shortened_url'
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2000), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.relationship('Click', backref='url', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'short_code': self.short_code,
            'original_url': self.original_url,
            'created_at': self.created_at.isoformat(),
            'total_clicks': len(self.clicks)
        }


class Click(db.Model):
    __tablename__ = 'click'
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('shortened_url.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    device_type = db.Column(db.String(50))
    device_brand = db.Column(db.String(100))
    device_model = db.Column(db.String(100))
    os_name = db.Column(db.String(100))
    os_version = db.Column(db.String(100))
    browser_name = db.Column(db.String(100))
    browser_version = db.Column(db.String(100))
    network_type = db.Column(db.String(50))
    screen_resolution = db.Column(db.String(50))
    timezone = db.Column(db.String(100))
    language = db.Column(db.String(50))
    cpu_cores = db.Column(db.Integer)
    device_memory = db.Column(db.Float)
    battery_level = db.Column(db.String(50))
    color_depth = db.Column(db.String(50))
    is_bot = db.Column(db.Boolean)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'ip_address': self.ip_address,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'device_type': self.device_type,
            'device_brand': self.device_brand,
            'device_model': self.device_model,
            'os': f"{self.os_name} {self.os_version}",
            'browser': f"{self.browser_name} {self.browser_version}",
            'network_type': self.network_type,
            'screen_resolution': self.screen_resolution,
            'timezone': self.timezone,
            'language': self.language,
            'cpu_cores': self.cpu_cores,
            'device_memory': self.device_memory,
            'battery_level': self.battery_level,
            'color_depth': self.color_depth,
            'is_bot': self.is_bot,
            'clicked_at': self.clicked_at.isoformat()
        }


# Utility Functions

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_slug(original_url):
    """Create a human-readable slug based on the hostname/path."""
    from urllib.parse import urlparse
    parsed = urlparse(original_url)
    hostname = parsed.hostname or ''
    # remove subdomains and tld
    parts = hostname.split('.')
    if len(parts) > 2:
        parts = parts[-2:]
    base = ''.join(ch for ch in parts[0] if ch.isalnum())
    if not base:
        base = generate_short_code(4)
    # limit length
    base = base[:12]
    slug = base
    # if conflict or slug already used, append random digits
    while ShortenedURL.query.filter_by(short_code=slug).first():
        slug = base + generate_short_code(2)
    return slug


def get_geolocation(ip_address):
    """Get geolocation from IP address"""
    try:
        # Using ip-api.com (free tier available)
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'location': f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}",
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'network_type': data.get('isp', 'Unknown')
                }
    except Exception as e:
        app.logger.error(f"Geolocation lookup error: {e}")
    
    return {
        'location': 'Unknown',
        'latitude': None,
        'longitude': None,
        'network_type': 'Unknown'
    }


def parse_user_agent(user_agent_string):
    """Parse user agent string to extract device and browser info"""
    ua = parse(user_agent_string)
    
    return {
        'device_type': ua.device.family or 'Unknown',
        'device_brand': ua.device.brand or 'Unknown',
        'device_model': ua.device.model or 'Unknown',
        'os_name': ua.os.family or 'Unknown',
        'os_version': ua.os.version_string or 'Unknown',
        'browser_name': ua.browser.family or 'Unknown',
        'browser_version': ua.browser.version_string or 'Unknown'
    }


def get_client_ip(request_obj):
    """Get the real public IP address, checking all common proxy headers."""
    # Cloudflare
    ip = request_obj.headers.get('CF-Connecting-IP')
    if ip:
        return ip.strip()
    # Nginx / standard reverse proxy
    ip = request_obj.headers.get('X-Real-IP')
    if ip:
        return ip.strip()
    # Load balancers (comma-separated list; first is the original client)
    ip = request_obj.headers.get('X-Forwarded-For')
    if ip:
        return ip.split(',')[0].strip()
    return request_obj.remote_addr


# API Routes
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Create a shortened URL or accept a custom alias"""
    data = request.get_json()
    original_url = data.get('url')
    custom_code = data.get('custom_code')  # optional
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL format (keep user string if it already includes protocol)
    if not (original_url.startswith('http://') or original_url.startswith('https://')):
        original_url = 'https://' + original_url
    
    # allow custom codes (alphanumeric only, length limit)
    if custom_code:
        if not custom_code.isalnum() or len(custom_code) > 20:
            return jsonify({'error': 'custom_code must be alphanumeric and <=20 chars'}), 400
        if ShortenedURL.query.filter_by(short_code=custom_code).first():
            return jsonify({'error': 'custom_code already in use'}), 409
        short_code = custom_code
    else:
        # Check if URL already shortened (only for automatically generated)
        existing = ShortenedURL.query.filter_by(original_url=original_url).first()
        if existing:
            return jsonify({
                'short_url': f"http://localhost:5000/{existing.short_code}",
                'short_code': existing.short_code,
                'original_url': existing.original_url
            })
        # generate a more readable slug based on url
        short_code = generate_slug(original_url)
    
    # Save to database
    shortened = ShortenedURL(original_url=original_url, short_code=short_code)
    db.session.add(shortened)
    db.session.commit()
    
    return jsonify({
        'short_url': f"http://localhost:5000/{short_code}",
        'short_code': short_code,
        'original_url': original_url
    }), 201


@app.route('/')
def home():
    """Serve the main terminal interface"""
    return render_template('index.html')


@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    """Show intermediate collector page that logs extra info, then redirect."""
    shortened = ShortenedURL.query.filter_by(short_code=short_code).first()
    if not shortened:
        return jsonify({'error': 'URL not found'}), 404
    # render page which will call /api/click and then change location
    return render_template('collector.html', short_code=short_code, original_url=shortened.original_url)


@app.route('/api/click/<short_code>', methods=['POST'])
def api_click(short_code):
    """Record a click with optional client-supplied geolocation/network data."""
    shortened = ShortenedURL.query.filter_by(short_code=short_code).first()
    if not shortened:
        return jsonify({'error': 'URL not found'}), 404
    data = request.get_json() or {}
    client_ip = get_client_ip(request)
    user_agent = data.get('user_agent', request.headers.get('User-Agent', ''))
    geo_data = get_geolocation(client_ip)
    
    # prefer client values if present
    latitude = data.get('latitude') or geo_data['latitude']
    longitude = data.get('longitude') or geo_data['longitude']
    location = data.get('location') or geo_data['location']
    network_type = data.get('network_type') or geo_data['network_type']
    
    device_data = parse_user_agent(user_agent)
    # override if client provided explicit fields
    if data.get('device_type'):
        device_data['device_type'] = data['device_type']
    if data.get('device_brand'):
        device_data['device_brand'] = data['device_brand']
    if data.get('device_model'):
        device_data['device_model'] = data['device_model']
    if data.get('os_name'):
        device_data['os_name'] = data['os_name']
    if data.get('os_version'):
        device_data['os_version'] = data['os_version']
    if data.get('browser_name'):
        device_data['browser_name'] = data['browser_name']
    if data.get('browser_version'):
        device_data['browser_version'] = data['browser_version']
    
    click = Click(
        url_id=shortened.id,
        ip_address=client_ip,
        user_agent=user_agent,
        location=location,
        latitude=latitude,
        longitude=longitude,
        network_type=network_type,
        screen_resolution=data.get('screen_resolution'),
        timezone=data.get('timezone'),
        language=data.get('language'),
        cpu_cores=data.get('cpu_cores'),
        device_memory=data.get('device_memory'),
        battery_level=str(data.get('battery_level', 'Unknown')),
        color_depth=str(data.get('color_depth', 'Unknown')),
        is_bot=bool(data.get('is_bot', False)),
        **device_data
    )
    db.session.add(click)
    db.session.commit()
    return jsonify({'status': 'ok'})


@app.route('/api/analytics/<short_code>', methods=['GET'])
def get_analytics(short_code):
    """Get analytics for a shortened URL"""
    shortened = ShortenedURL.query.filter_by(short_code=short_code).first()
    
    if not shortened:
        return jsonify({'error': 'URL not found'}), 404
    
    clicks = Click.query.filter_by(url_id=shortened.id).all()
    
    return jsonify({
        'short_code': short_code,
        'original_url': shortened.original_url,
        'created_at': shortened.created_at.isoformat(),
        'total_clicks': len(clicks),
        'clicks': [click.to_dict() for click in clicks]
    })


@app.route('/api/urls', methods=['GET'])
def list_urls():
    """List all shortened URLs"""
    urls = ShortenedURL.query.all()
    return jsonify([url.to_dict() for url in urls])


@app.route('/api/all_clicks', methods=['GET'])
def get_all_clicks():
    """Get all clicks across all shortened URLs"""
    urls = ShortenedURL.query.all()
    all_clicks = []
    
    for url in urls:
        clicks = Click.query.filter_by(url_id=url.id).all()
        for click in clicks:
            c_dict = click.to_dict()
            c_dict['short_code'] = url.short_code
            c_dict['original_url'] = url.original_url
            all_clicks.append(c_dict)
            
    return jsonify({
        'total_clicks': len(all_clicks),
        'clicks': all_clicks
    })
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
