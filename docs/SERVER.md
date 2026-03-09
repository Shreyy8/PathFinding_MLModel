# Interactive Road Mapping Interface - Backend API Server

This document describes how to run and configure the Backend API Server for the Interactive Road Mapping Interface.

## Overview

The Backend API Server provides REST endpoints for:
- Loading and processing satellite images
- Road segmentation using deep learning models
- Graph construction from road masks
- Pathfinding between start and goal points
- Session management for multiple users

## Prerequisites

- Python 3.8 or higher
- Required Python packages (see `requirements.txt`)
- Trained model checkpoint (optional, for road segmentation)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## Running the Server

### Basic Usage

Start the server with default settings (localhost:5000):
```bash
python run_server.py
```

### Custom Configuration

#### Using Command-Line Arguments

```bash
# Bind to all network interfaces
python run_server.py --host 0.0.0.0

# Use custom port
python run_server.py --port 8080

# Enable debug mode
python run_server.py --debug

# Disable debug mode explicitly
python run_server.py --no-debug

# Combine options
python run_server.py --host 0.0.0.0 --port 8080 --debug
```

#### Using Environment Variables

Set environment variables before running:
```bash
# Linux/Mac
export API_HOST=0.0.0.0
export API_PORT=8080
export API_DEBUG=True
python run_server.py

# Windows (Command Prompt)
set API_HOST=0.0.0.0
set API_PORT=8080
set API_DEBUG=True
python run_server.py

# Windows (PowerShell)
$env:API_HOST="0.0.0.0"
$env:API_PORT="8080"
$env:API_DEBUG="True"
python run_server.py
```

#### Using .env File

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
API_HOST=0.0.0.0
API_PORT=8080
API_DEBUG=False
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
LOG_LEVEL=INFO
MODEL_CHECKPOINT_PATH=models/best_model.pth
```

Then run:
```bash
python run_server.py
```

## Configuration Options

### Server Settings

- `API_HOST`: Host address to bind to (default: `localhost`)
  - Use `localhost` for local development
  - Use `0.0.0.0` to accept connections from any network interface
  
- `API_PORT`: Port number to bind to (default: `5000`)
  
- `API_DEBUG`: Enable Flask debug mode (default: `False`)
  - Set to `True` for development (auto-reload, detailed errors)
  - Set to `False` for production

### CORS Settings

- `CORS_ORIGINS`: Comma-separated list of allowed origins
  - Development: `http://localhost:*,http://127.0.0.1:*`
  - Production: Specify exact origins (e.g., `http://example.com:3000`)

### Image Processing

- `MAX_IMAGE_SIZE`: Maximum image file size in bytes (default: 10 MB)
- `MAX_IMAGE_DIMENSION`: Maximum image dimension in pixels (default: 4096)

### Session Management

- `SESSION_TIMEOUT`: Session timeout in seconds (default: 3600 = 1 hour)

### Logging

- `LOG_LEVEL`: Logging level (default: `INFO`)
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Model Settings

- `MODEL_CHECKPOINT_PATH`: Path to trained model checkpoint (default: `models/best_model.pth`)
  - If file doesn't exist, server will start with untrained model

## API Endpoints

### Health Check
```
GET /api/health
```
Returns server health status.

### Load Image
```
POST /api/load-image
Content-Type: multipart/form-data
Body: image=<file>
```
Uploads and processes a satellite image, performs road segmentation, and constructs road graph.

### Select Start Point
```
POST /api/select-start
Content-Type: application/json
Body: {"image_id": "...", "x": 100, "y": 200}
```
Selects a start point for pathfinding.

### Select Goal Point
```
POST /api/select-goal
Content-Type: application/json
Body: {"image_id": "...", "x": 300, "y": 400}
```
Selects a goal point and computes shortest path if start point exists.

### Clear Selection
```
POST /api/clear-selection
Content-Type: application/json
Body: {"image_id": "..."}
```
Clears start point, goal point, and path for a session.

### Get State
```
GET /api/state/<image_id>
```
Retrieves current state for a session.

## Development

### Running in Debug Mode

Debug mode enables:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

```bash
python run_server.py --debug
```

**Warning:** Never use debug mode in production!

### Logging

Logs are written to stdout. To save logs to a file:
```bash
python run_server.py > server.log 2>&1
```

To see detailed debug logs:
```bash
export LOG_LEVEL=DEBUG
python run_server.py
```

## Production Deployment

For production deployment, use a production WSGI server like Gunicorn or uWSGI instead of the Flask development server.

### Using Gunicorn

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create a WSGI entry point (`wsgi.py`):
```python
from src.main import create_app

app = create_app().get_app()

if __name__ == '__main__':
    app.run()
```

3. Run with Gunicorn:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### Production Checklist

- [ ] Set `API_DEBUG=False`
- [ ] Configure specific CORS origins (no wildcards)
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx, Apache)
- [ ] Configure SSL/TLS certificates
- [ ] Set up logging to files
- [ ] Configure firewall rules
- [ ] Set appropriate resource limits
- [ ] Monitor server health and performance

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:
```bash
# Find process using the port (Linux/Mac)
lsof -i :5000

# Find process using the port (Windows)
netstat -ano | findstr :5000

# Kill the process or use a different port
python run_server.py --port 8080
```

### Model Checkpoint Not Found

If you see "Model checkpoint not found" warning:
- The server will start with an untrained model
- To use a trained model, place checkpoint at `models/best_model.pth`
- Or set `MODEL_CHECKPOINT_PATH` to your checkpoint location

### CORS Errors

If frontend can't connect due to CORS:
- Check `CORS_ORIGINS` includes your frontend URL
- For development, use wildcard: `http://localhost:*`
- For production, specify exact origin: `http://example.com:3000`

### Import Errors

If you see module import errors:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)
- Verify you're in the correct directory

## Support

For issues and questions:
- Check the logs for detailed error messages
- Review the API documentation
- Ensure all prerequisites are met
- Verify configuration settings

## License

[Your License Here]
