# Getting Started

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm, pnpm, or yarn
- 4GB RAM minimum
- 10GB disk space

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd road-mapping-interface
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import torch; import flask; print('Backend dependencies OK')"
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

## Configuration

### Backend Configuration

Edit `backend/src/api/config.py` or set environment variables:

```bash
# Server settings
export API_HOST=localhost
export API_PORT=5000
export API_DEBUG=False

# CORS settings
export CORS_ORIGINS=http://localhost:3000

# Image limits
export MAX_IMAGE_SIZE=10485760  # 10MB
export MAX_IMAGE_DIMENSION=4096

# Model path
export MODEL_CHECKPOINT_PATH=models/best_model.pth
```

### Frontend Configuration

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## Running the Application

### Development Mode

**Option 1: Automated (Recommended)**

```bash
# Linux/Mac
./scripts/start.sh

# Windows
scripts\start.bat
```

**Option 2: Manual**

Terminal 1 - Backend:
```bash
python run_server.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Application

Open your browser to: http://localhost:3000

## First Steps

1. **Upload an Image**
   - Click "Upload Image"
   - Select a satellite/aerial image
   - Wait for processing (2-5 seconds)

2. **View Road Network**
   - Red overlay shows detected roads
   - Adjust opacity with slider
   - Toggle overlay visibility

3. **Select Points**
   - Click on a road for start point (green marker)
   - Click on another road for goal point (red marker)
   - Path automatically computes (blue line)

4. **View Statistics**
   - See road coverage percentage
   - View path length and waypoints
   - Check graph complexity

## Verification

### Test Backend

```bash
# Test backend connectivity
python scripts/test_connection.py

# Or manually
curl http://localhost:5000/api/state/test
```

### Test Frontend

```bash
cd frontend
npm run lint
npm run build
```

## Common Issues

### Backend Won't Start

**Issue:** Port 5000 already in use

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Frontend Won't Connect

**Issue:** CORS errors

**Solution:** Verify CORS_ORIGINS includes frontend URL

### Model Not Found

**Issue:** Model checkpoint missing

**Solution:** Ensure `models/best_model.pth` exists or update path in config

## Next Steps

- Read [API Documentation](API.md) for endpoint details
- Review [Architecture](ARCHITECTURE.md) for system design
- Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
- See [Deployment](DEPLOYMENT.md) for production setup

## Support

For issues and questions:
1. Check [Troubleshooting](TROUBLESHOOTING.md)
2. Review error logs
3. Check browser console (F12)
4. Verify both servers are running
