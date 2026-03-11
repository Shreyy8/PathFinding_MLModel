# System Overview - Interactive Road Mapping Interface

## 🎯 What Does This System Do?

This is a complete web application that allows users to:
1. Upload satellite/aerial images
2. Automatically detect roads using AI
3. Click on the map to select start and destination points
4. See the shortest path between those points

Think of it like Google Maps, but for custom satellite imagery!

## 🏗️ System Components

### Frontend (What Users See)
**Technology:** Next.js + React + TypeScript
**Location:** `v0-road-mapping-interface-main/`

```
┌─────────────────────────────────────────────┐
│         Browser (localhost:3000)            │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  Upload Image Button                  │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │                                       │ │
│  │   Satellite Image Display             │ │
│  │   + Red Road Overlay                  │ │
│  │   + Green Start Marker (S)            │ │
│  │   + Red Goal Marker (G)               │ │
│  │   + Blue Path Line                    │ │
│  │                                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │  Controls:                            │ │
│  │  - Overlay Opacity Slider             │ │
│  │  - Clear Selection Button             │ │
│  │  - Status Indicators                  │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Backend API (The Brain)
**Technology:** Python + Flask
**Location:** `src/api/`

```
┌─────────────────────────────────────────────┐
│      Flask Server (localhost:5000)          │
│                                             │
│  REST API Endpoints:                        │
│  ├─ POST /api/load-image                   │
│  ├─ POST /api/select-start                 │
│  ├─ POST /api/select-goal                  │
│  ├─ POST /api/clear-selection              │
│  └─ GET  /api/state/{image_id}             │
│                                             │
│  Components:                                │
│  ├─ StateManager (session storage)         │
│  ├─ ImageProcessor (image handling)        │
│  ├─ PointValidator (click validation)      │
│  └─ PathfindingCoordinator (path compute)  │
└─────────────────────────────────────────────┘
```

### Core Processing Engines
**Technology:** Python + PyTorch + NetworkX
**Location:** `src/`

```
┌─────────────────────────────────────────────┐
│         Processing Components               │
│                                             │
│  1. RoadSegmentationModel                  │
│     - Deep learning (PyTorch)              │
│     - Identifies road pixels               │
│     - Input: Satellite image               │
│     - Output: Binary road mask             │
│                                             │
│  2. GraphConstructor                       │
│     - Converts mask to graph               │
│     - Input: Road mask                     │
│     - Output: Graph (nodes + edges)        │
│                                             │
│  3. PathfindingEngine                      │
│     - A* / Dijkstra algorithm              │
│     - Input: Graph + start + goal          │
│     - Output: Shortest path                │
└─────────────────────────────────────────────┘
```

## 🔄 Complete Workflow

### Step 1: Image Upload
```
User clicks "Upload Image"
    ↓
Frontend sends image to backend
    ↓
Backend receives image
    ↓
ImageProcessor validates image
    ↓
RoadSegmentationModel processes image
    ↓
GraphConstructor builds road graph
    ↓
StateManager stores session data
    ↓
Backend returns: image_id, image_data, road_mask_data
    ↓
Frontend displays image + road overlay
```

### Step 2: Start Point Selection
```
User clicks on map
    ↓
Frontend captures click coordinates (x, y)
    ↓
Frontend sends coordinates to backend
    ↓
PointValidator checks if point is on road
    ↓
If valid:
    StateManager stores start point
    Backend returns: {valid: true}
    Frontend displays green "S" marker
If invalid:
    Backend returns: {valid: false, error: "Not on road"}
    Frontend shows error notification
```

### Step 3: Goal Point Selection
```
User clicks on map again
    ↓
Frontend captures click coordinates (x, y)
    ↓
Frontend sends coordinates to backend
    ↓
PointValidator checks if point is on road
    ↓
If valid:
    StateManager stores goal point
    PathfindingEngine computes shortest path
    Backend returns: {valid: true, path: [...]}
    Frontend displays:
        - Red "G" marker
        - Blue path line
If invalid:
    Backend returns: {valid: false, error: "Not on road"}
    Frontend shows error notification
```

### Step 4: Clear and Retry
```
User clicks "Clear Selection"
    ↓
Frontend sends clear request to backend
    ↓
StateManager clears start, goal, and path
    ↓
Backend returns: {message: "Selection cleared"}
    ↓
Frontend removes markers and path
    ↓
User can select new points
```

## 📊 Data Flow Diagram

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Upload Image
     ↓
┌────────────────┐      2. Process Image      ┌──────────────────┐
│   Frontend     │ ────────────────────────→  │   Backend API    │
│  (Next.js)     │                             │    (Flask)       │
│                │ ←────────────────────────   │                  │
│  - Canvas      │   3. Return image_id +      │  - StateManager  │
│  - Markers     │      image + mask           │  - Validator     │
│  - Path        │                             │  - Coordinator   │
└────────────────┘                             └────────┬─────────┘
     │                                                  │
     │ 4. Click (x,y)                                  │
     │ ────────────────────────────────────────────→   │
     │                                                  │ 5. Validate
     │                                                  ↓
     │                                         ┌─────────────────┐
     │                                         │  Core Engines   │
     │                                         │                 │
     │                                         │  - Segmentation │
     │                                         │  - Graph Build  │
     │                                         │  - Pathfinding  │
     │                                         └─────────────────┘
     │                                                  │
     │ ←────────────────────────────────────────────   │
     │   6. Return validation + path                   │
     │                                                  │
     ↓ 7. Display markers + path
┌────────────────┐
│  User sees     │
│  visual result │
└────────────────┘
```

## 🗂️ File Organization

```
Project Root
│
├── Backend (Python)
│   ├── src/
│   │   ├── api/                    # Flask API layer
│   │   │   ├── app.py             # Main Flask app
│   │   │   ├── state_manager.py   # Session management
│   │   │   ├── point_validator.py # Point validation
│   │   │   ├── image_processor.py # Image handling
│   │   │   └── pathfinding_coordinator.py
│   │   │
│   │   ├── road_segmentation_model.py  # AI model
│   │   ├── graph_constructor.py        # Graph builder
│   │   └── pathfinding_engine.py       # A* algorithm
│   │
│   ├── tests/                     # Backend tests
│   ├── models/                    # Model weights
│   └── run_server.py             # Backend entry point
│
├── Frontend (Next.js)
│   └── v0-road-mapping-interface-main/
│       ├── app/                   # Next.js pages
│       │   └── page.tsx          # Main page
│       │
│       ├── components/            # React components
│       │   ├── map-canvas.tsx    # Canvas visualization
│       │   ├── controls-panel.tsx # Control panel
│       │   └── notifications.tsx  # Toast system
│       │
│       └── lib/
│           └── api-client.ts     # Backend API client
│
└── Documentation
    ├── README_FULLSTACK.md       # Complete guide
    ├── FRONTEND_INTEGRATION_GUIDE.md
    ├── SYSTEM_OVERVIEW.md        # This file
    └── start_full_stack.sh       # Startup script
```

## 🎨 Visual Components

### Canvas Layers (Frontend)
The frontend uses 4 stacked canvas layers for optimal performance:

```
Layer 4 (Top)    ┌─────────────────────┐
Markers          │  🟢 S      🔴 G     │  ← Start/Goal markers
                 └─────────────────────┘

Layer 3          ┌─────────────────────┐
Path             │    ╱╲  ╱╲  ╱╲       │  ← Blue path line
                 └─────────────────────┘

Layer 2          ┌─────────────────────┐
Road Overlay     │  ▓▓▓░░▓▓▓░░▓▓▓      │  ← Red semi-transparent
                 └─────────────────────┘

Layer 1 (Bottom) ┌─────────────────────┐
Satellite Image  │  [Satellite Photo]  │  ← Base image
                 └─────────────────────┘
```

### State Machine (Frontend)
```
┌──────────┐
│   IDLE   │  ← Initial state
└────┬─────┘
     │ Image uploaded
     ↓
┌──────────────────┐
│ SELECTING_START  │  ← Waiting for start point click
└────┬─────────────┘
     │ Valid start point clicked
     ↓
┌──────────────────┐
│ SELECTING_GOAL   │  ← Waiting for goal point click
└────┬─────────────┘
     │ Valid goal point clicked
     ↓
┌──────────┐
│   IDLE   │  ← Path displayed, can reselect
└──────────┘
```

## 🔐 Security & Validation

### Input Validation
```
Frontend Validation:
├─ File type check (image/*)
├─ File size check (<10MB)
└─ Coordinate bounds check

Backend Validation:
├─ Image format validation (PIL)
├─ Image dimension check (<4096px)
├─ Point on road validation (mask check)
└─ Session ID validation (UUID)
```

### Error Handling
```
Error Types:
├─ Network errors (connection failed)
├─ Validation errors (invalid point)
├─ Processing errors (segmentation failed)
└─ Not found errors (invalid session)

Error Display:
├─ Toast notifications (frontend)
├─ HTTP status codes (API)
└─ Detailed logs (backend)
```

## 📈 Performance Characteristics

### Backend Processing Times
```
Image Upload & Processing:
├─ Image validation:        <100ms
├─ Road segmentation:        2-5 seconds
├─ Graph construction:       500ms-2s
└─ Total:                    3-7 seconds

Point Selection:
├─ Point validation:         <10ms
├─ Pathfinding:             50-500ms
└─ Total:                    <1 second
```

### Frontend Rendering
```
Canvas Operations:
├─ Image load:              <500ms
├─ Overlay render:          <100ms
├─ Marker draw:             <50ms
├─ Path draw:               <100ms
└─ Frame rate:              60 FPS
```

## 🌐 Network Communication

### API Request/Response Format

**Example: Load Image**
```
Request:
POST /api/load-image
Content-Type: multipart/form-data
Body: [image file]

Response:
{
  "image_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "road_mask_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "width": 1024,
  "height": 768,
  "message": "Image processed successfully"
}
```

**Example: Select Point**
```
Request:
POST /api/select-start
Content-Type: application/json
{
  "image_id": "550e8400-e29b-41d4-a716-446655440000",
  "x": 512,
  "y": 384
}

Response (Valid):
{
  "valid": true,
  "coordinates": {"x": 512, "y": 384},
  "message": "Start point selected"
}

Response (Invalid):
{
  "valid": false,
  "error": "Point is not on a road",
  "coordinates": {"x": 512, "y": 384}
}
```

## 🎯 Key Design Decisions

### Why Separate Frontend and Backend?
- **Scalability:** Can scale independently
- **Technology Choice:** Best tool for each job
- **Development:** Teams can work in parallel
- **Deployment:** Deploy to different platforms

### Why Canvas Instead of SVG?
- **Performance:** Better for large images
- **Pixel Precision:** Exact coordinate mapping
- **Layering:** Easy to manage multiple layers
- **Rendering Speed:** Faster for complex paths

### Why Flask Instead of FastAPI?
- **Simplicity:** Easier to understand
- **Maturity:** Well-established ecosystem
- **Compatibility:** Works with existing code
- **Sufficient:** Meets performance requirements

### Why Next.js Instead of Plain React?
- **SSR/SSG:** Better performance
- **Routing:** Built-in file-based routing
- **Optimization:** Automatic code splitting
- **Developer Experience:** Hot reload, TypeScript support

## 🚀 Getting Started (Quick Version)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
   npm install
   cd ../..
   ```

2. **Start servers:**
   ```bash
   # Linux/Mac
   ./start_full_stack.sh
   
   # Windows
   start_full_stack.bat
   ```

3. **Open browser:**
   ```
   http://localhost:3000
   ```

4. **Upload an image and start mapping!**

