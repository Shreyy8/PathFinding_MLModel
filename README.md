# Interactive Road Mapping Interface

A production-ready full-stack web application for interactive road mapping and pathfinding on satellite imagery.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This application combines computer vision, graph algorithms, and an intuitive web interface to enable:
- **AI-Powered Road Detection** using deep learning (PyTorch)
- **Interactive Point Selection** with real-time validation
- **Optimal Path Computation** using A* algorithm
- **Real-Time Visualization** with detailed statistics

## ✨ Features

- 🛣️ Automatic road segmentation from satellite imagery
- 🗺️ Interactive map interface with click-to-select waypoints
- 🎯 Shortest path computation with A* pathfinding
- 📊 Detailed statistics (coverage, path length, graph metrics)
- 🎨 Responsive design (desktop, tablet, mobile)
- ⚡ Real-time updates and visualization
- 🔒 Production-ready with comprehensive error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- 4GB RAM
- 10GB disk space

### Installation

```bash
# 1. Install backend dependencies
pip install -r requirements.txt

# 2. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running

**Automated (Recommended):**
```bash
# Linux/Mac
./scripts/start.sh

# Windows
scripts\start.bat
```

**Manual:**
```bash
# Terminal 1 - Backend
python run_server.py

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**Access:** http://localhost:3000

## 📁 Project Structure

```
road-mapping-interface/
├── backend/
│   ├── src/
│   │   ├── api/              # REST API implementation
│   │   ├── *.py              # Core modules (segmentation, pathfinding, etc.)
│   │   └── __init__.py
│   ├── tests/                # Comprehensive test suite
│   ├── models/               # Model weights
│   └── requirements.txt
├── frontend/
│   ├── app/                  # Next.js pages
│   ├── components/           # React components
│   ├── lib/                  # Utilities and API client
│   └── package.json
├── docs/                     # Documentation
│   ├── GETTING_STARTED.md
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
├── scripts/                  # Utility scripts
│   ├── start.sh
│   ├── start.bat
│   └── cleanup.py
├── .env.example              # Environment variables template
├── run_server.py             # Backend entry point
└── README.md                 # This file
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  - React Components                                         │
│  - Canvas Visualization                                     │
│  - Interactive UI                                           │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (HTTP/JSON)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Backend API (Flask)                       │
│  - Image Processing                                         │
│  - State Management                                         │
│  - Point Validation                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼────────────┐
│ Road Seg.    │ │ Graph   │ │ Pathfinding   │
│ (PyTorch)    │ │ Builder │ │ (A*)          │
└──────────────┘ └─────────┘ └───────────────┘
```

## 📖 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Setup and installation
- **[API Reference](docs/API.md)** - Backend API endpoints
- **[Architecture](docs/ARCHITECTURE.md)** - System design
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/test_api_setup.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🚢 Deployment

### Backend

```bash
# Production server
gunicorn -w 4 -b 0.0.0.0:5000 'src.api.app:create_app()'
```

### Frontend

```bash
cd frontend
npm run build
npm start
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 🛠️ Technology Stack

**Backend:**
- Python 3.8+
- Flask (REST API)
- PyTorch (Deep Learning)
- NetworkX (Graph Algorithms)
- NumPy, OpenCV, Pillow

**Frontend:**
- Next.js 16 + React 19
- TypeScript
- Tailwind CSS
- shadcn/ui Components

**Algorithms:**
- Road Segmentation: U-Net with ResNet34 encoder
- Pathfinding: A* with Euclidean heuristic
- Graph Construction: 8-connectivity

## 📊 Performance

- Image Processing: 2-5 seconds
- Point Validation: <10ms
- Pathfinding: 50-500ms
- Memory Usage: ~500MB (backend), ~100MB (frontend)

## 🔒 Security

- Input validation on all endpoints
- CORS configuration
- File size limits (10MB)
- Session management
- Error handling without sensitive data exposure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

[Your License Here]

## 👥 Authors

[Your Team/Contributors Here]

## 🙏 Acknowledgments

- PyTorch for deep learning framework
- Next.js for frontend framework
- Flask for backend API
- shadcn/ui for UI components

## 📞 Support

- **Documentation:** See [docs/](docs/)
- **Issues:** [GitHub Issues](your-repo-url/issues)
- **Email:** [your-email]

---

**Made with ❤️ for mission planning and route optimization**
