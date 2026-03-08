# ⚡ Quick Start Guide

## 1️⃣ First Time Setup

### Windows
```bash
# Run the batch file
run.bat
```

### macOS/Linux
```bash
# Make the script executable
chmod +x run.sh

# Run it
./run.sh
```

### Or Use Python Setup
```bash
python setup.py
```

---

## 2️⃣ Starting the Application

### After Setup (Windows)
```bash
# Just double-click run.bat
# Or in PowerShell:
.\run.bat
```

### After Setup (macOS/Linux)
```bash
# Activate virtual environment
source venv/bin/activate

# Start the app
python app.py
```

---

## 3️⃣ Access the Dashboard

Open your browser and go to:
```
http://localhost:5000/dashboard
```

---

## 4️⃣ Using the Application

### Shorten a URL
1. Paste any long URL in the input box
2. Click "Shorten"
3. Copy the short link that appears

### Share Your Link
- Copy the short link (e.g., `http://localhost:5000/abc123`)
- Share it on social media, email, chat, etc.
- When friends click it, they'll be redirected to your original URL

### View Analytics
1. Go to the dashboard
2. Find your link in "Your Shortened Links"
3. Click "Analytics" to see:
   - Total clicks
   - Visitor locations
   - Device types & specs
   - Operating systems
   - Browsers used
   - Network providers

---

## 5️⃣ What Data Is Tracked?

When someone clicks your link, we track:

**📍 Location**
- City, Region, Country
- GPS Coordinates (Latitude/Longitude)
- ISP/Network Provider

**📱 Device**
- Type (Mobile, Desktop, Tablet)
- Brand & Model
- Operating System & Version

**🌐 Browser**
- Browser Name & Version
- IP Address
- Timestamp

---

## 6️⃣ API Usage (for Developers)

### Shorten a URL
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/long/url"}'
```

### Get Analytics
```bash
curl http://localhost:5000/api/analytics/abc123
```

### List All URLs
```bash
curl http://localhost:5000/api/urls
```

---

## 7️⃣ Troubleshooting

### Application Won't Start?
1. Make sure Python 3.7+ is installed
2. Delete the `venv` folder and run setup again
3. Check if port 5000 is available

### Can't Find My Links?
- Links are stored in `locator.db`
- Don't delete this file!
- If deleted, previous links will be lost

### Geolocation Shows "Unknown"?
- Geolocation doesn't work for local IPs (127.0.0.1, 192.168.x.x)
- It needs to be accessed from external networks
- Or use VPN to test

### Can I Access from Another Computer?
Yes! Find your IP address and use:
```
http://<YOUR_IP>:5000/dashboard
```

---

## 8️⃣ Tips & Tricks

✅ Use descriptive URLs that hint at the destination  
✅ Track campaigns by creating different links for each channel  
✅ Share analytics with colleagues to track content performance  
✅ Copy links to clipboard with one click  
✅ Link data persists even if you restart the app  

---

## 9️⃣ Advanced: Changing the Port

Edit `app.py` at the bottom:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

Then restart the app and visit:
```
http://localhost:8000/dashboard
```

---

## 🔟 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the [API endpoints](README.md#api-endpoints)
- Customize the app for your needs!

---

**Happy link shortening! 🚀**
