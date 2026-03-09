# Interactive Road Mapping Interface - Documentation

## Quick Links

- [Getting Started](GETTING_STARTED.md) - Setup and installation
- [API Documentation](API.md) - Backend API reference
- [Architecture](ARCHITECTURE.md) - System design and components
- [Deployment](DEPLOYMENT.md) - Production deployment guide
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Project Overview

A full-stack web application for interactive road mapping and pathfinding on satellite imagery, combining computer vision (road segmentation), graph algorithms (A* pathfinding), and an intuitive web interface.

## Features

- AI-powered road detection using deep learning
- Interactive point selection with validation
- Shortest path computation (A* algorithm)
- Real-time path visualization
- Detailed statistics and metrics
- Responsive web interface

## Technology Stack

**Backend:**
- Python 3.8+
- Flask (REST API)
- PyTorch (Deep Learning)
- NetworkX (Graph algorithms)
- NumPy, OpenCV, Pillow

**Frontend:**
- Next.js 16 + React 19
- TypeScript
- Tailwind CSS
- shadcn/ui components

## Project Structure

```
road-mapping-interface/
├── backend/              # Python backend
│   ├── src/             # Source code
│   ├── tests/           # Test suite
│   ├── models/          # Model weights
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/            # Pages
│   ├── components/     # React components
│   └── lib/            # Utilities
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Start Servers

**Backend:**
```bash
python run_server.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Open Application

Navigate to: http://localhost:3000

## Documentation

See the [docs](.) folder for detailed documentation on:
- Setup and configuration
- API endpoints
- Architecture and design
- Deployment strategies
- Troubleshooting

## License

[Your License Here]

## Contributors

[Your Team/Contributors Here]
