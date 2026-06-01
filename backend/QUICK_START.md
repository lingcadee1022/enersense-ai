# EnerSense AI Backend - Quick Start Guide

Get the FastAPI backend running in 5 minutes.

## Prerequisites

- Python 3.8+
- MongoDB running locally or access to MongoDB Atlas
- Git

## Quick Setup (5 minutes)

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env (if using MongoDB Atlas instead of local)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/enersense
```

### 5. Start Server

```bash
python main.py
```

✅ **Server running at http://localhost:8000**

## Quick Test

### Test in Browser

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Custom Docs**: http://localhost:8000/docs-custom

### Test with cURL

```bash
# 1. Send sensor data
curl -X POST http://localhost:8000/api/v1/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"esp32_01","current":0.8,"power":180}'

# 2. Get live usage
curl http://localhost:8000/api/v1/live-usage?device_id=esp32_01

# 3. Get 24-hour history
curl http://localhost:8000/api/v1/history?device_id=esp32_01&hours=24

# 4. Generate AI insights
curl http://localhost:8000/api/v1/insights?device_id=esp32_01
```

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check |
| `/api/v1/sensor-data` | POST | Send sensor data |
| `/api/v1/live-usage` | GET | Latest reading |
| `/api/v1/history` | GET | Historical data |
| `/api/v1/insights` | GET | AI insights |

## Common Issues

### MongoDB Connection Failed

1. Check MongoDB is running:
   ```bash
   # Linux/Mac
   ps aux | grep mongod
   
   # Windows
   netstat -an | findstr :27017
   ```

2. Start MongoDB:
   ```bash
   mongod
   ```

3. Or use MongoDB Atlas and update `.env`:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/enersense
   ```

### Port 8000 Already in Use

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

## Next Steps

1. ✅ **Server is running** - Verify with http://localhost:8000/health
2. 📊 **Start sending data** - POST to /api/v1/sensor-data
3. 📈 **View insights** - GET /api/v1/insights
4. 🤖 **Train models** - POST /api/v1/insights/train-profile
5. 📚 **Read full docs** - See [README.md](README.md)

## Development Tips

### Enable Debug Logging

Edit `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Test with Python

```python
import requests

# Send data
data = {"device_id": "esp32_01", "current": 0.8, "power": 180}
r = requests.post("http://localhost:8000/api/v1/sensor-data", json=data)
print(r.json())

# Get insights
r = requests.get("http://localhost:8000/api/v1/insights?device_id=esp32_01")
print(r.json())
```

### Auto-reload During Development

Already enabled with `python main.py` - server reloads on file changes.

## Production Deployment

See [README.md - Deployment](README.md#deployment) for Docker and Kubernetes setup.

## Need Help?

1. Check MongoDB connection: `curl http://localhost:8000/health`
2. View API docs: http://localhost:8000/docs
3. Read [README.md](README.md) for full documentation
4. Check logs in terminal for error messages

---

**Happy coding! 🚀**
