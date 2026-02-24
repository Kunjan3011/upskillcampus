# Deployment Guide

## Local Development (No ngrok needed)

Your API is already running locally and accessible at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

### Accessing from Other Devices on Your Network

If you want to access the API from another device on the same network:

1. **Find your local IP address:**
   ```powershell
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

2. **Update API host in run_api.py:**
   ```python
   # Already set to 0.0.0.0 which allows network access
   uvicorn.run(
       "src.api.Agriculture_Crop_Production_Prediction_System:app",
       host="0.0.0.0",  # This allows network access
       port=8000,
       ...
   )
   ```

3. **Access from other device:**
   - API: `http://YOUR_IP:8000` (e.g., http://192.168.1.100:8000)
   - Dashboard: Update `API_BASE_URL` in `dashboard/app.py` to match

## Using ngrok (For Internet Access)

### When to Use ngrok:
- ✅ Share API with someone outside your network
- ✅ Test webhooks or external integrations
- ✅ Demo the API to clients/colleagues
- ✅ Mobile app testing from phone

### Installation:
```bash
# Download from https://ngrok.com/download
# Or use chocolatey on Windows:
choco install ngrok

# Or use pip:
pip install pyngrok
```

### Usage:

**Option 1: Command Line**
```bash
ngrok http 8000
```

**Option 2: Python Script**
```python
from pyngrok import ngrok

# Start ngrok tunnel
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")
```

### Update Dashboard for ngrok:
If using ngrok, update `dashboard/app.py`:
```python
API_BASE_URL = "https://your-ngrok-url.ngrok.io"  # Your ngrok URL
```

## Production Deployment (Better than ngrok)

For permanent deployment, consider:

### 1. **Cloud Platforms:**
- **Heroku**: Easy deployment
- **Railway**: Simple setup
- **Render**: Free tier available
- **AWS/GCP/Azure**: For production scale

### 2. **VPS/Server:**
- Use a VPS (DigitalOcean, Linode, etc.)
- Set up with Nginx reverse proxy
- Use domain name with SSL

### 3. **Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.Agriculture_Crop_Production_Prediction_System:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Considerations

⚠️ **Important**: If exposing your API publicly:

1. **Add Authentication:**
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **Rate Limiting:**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

3. **CORS Configuration:**
   ```python
   # Update CORS in src/api/main.py
   allow_origins=["https://yourdomain.com"]  # Specific domains
   ```

4. **Environment Variables:**
   - Don't hardcode secrets
   - Use `.env` file for configuration

## Quick Start for Local Network Access

1. **Find your IP:**
   ```powershell
   ipconfig | findstr IPv4
   ```

2. **Access from phone/other device:**
   - Make sure both devices on same WiFi
   - Open: `http://YOUR_IP:8000/docs`

3. **If firewall blocks:**
   ```powershell
   # Allow Python through firewall
   New-NetFirewallRule -DisplayName "Python API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

## Summary

- **Local development**: No ngrok needed ✅
- **Same network**: Use local IP, no ngrok needed ✅
- **Internet access**: Use ngrok or deploy to cloud
- **Production**: Deploy to cloud platform

Your current setup is perfect for local development!


