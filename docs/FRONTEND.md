# Frontend Integration Guide

## Overview

The frontend has been successfully added to the `v0-road-mapping-interface-main` folder. It's a modern Next.js/React application built with TypeScript that integrates with your Python backend API.

## Frontend Technology Stack

- **Framework:** Next.js 16 with React 19
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI + shadcn/ui
- **State Management:** React hooks
- **HTTP Client:** Fetch API

## Architecture

The frontend follows a clean component-based architecture:

```
v0-road-mapping-interface-main/
├── app/
│   ├── page.tsx              # Main application page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── map-canvas.tsx        # Canvas component for map visualization
│   ├── controls-panel.tsx    # Control panel with upload/settings
│   ├── notifications.tsx     # Toast notification system
│   └── ui/                   # Reusable UI components (shadcn)
├── lib/
│   ├── api-client.ts         # Backend API client
│   └── utils.ts              # Utility functions
└── hooks/
    ├── use-toast.ts          # Toast notification hook
    └── use-mobile.ts         # Mobile detection hook
```

## Key Features Implemented

✅ **Image Upload & Display**
- File upload with drag-and-drop support
- Base64 image rendering on HTML5 Canvas
- Responsive image display

✅ **Road Overlay Visualization**
- Semi-transparent road mask overlay
- Adjustable opacity slider (0-100%)
- Toggle overlay visibility

✅ **Interactive Point Selection**
- Click-to-select start and goal points
- Visual markers (green "S" for start, red "G" for goal)
- Point validation with error feedback

✅ **Path Visualization**
- Animated path rendering with glow effect
- Blue path line connecting start to goal
- Smooth canvas rendering

✅ **State Management**
- Selection mode tracking (idle → start → goal)
- Session state persistence
- Real-time UI updates

✅ **Error Handling**
- Toast notifications for success/error/info
- Network error handling
- Invalid point selection feedback

✅ **Responsive Design**
- Mobile-friendly layout
- Adaptive canvas sizing
- Touch-friendly controls

## API Integration

The frontend correctly implements all backend API endpoints:

### 1. POST /api/load-image
```typescript
await apiClient.loadImage(file)
// Returns: { image_id, image_data, road_mask_data, width, height }
```

### 2. POST /api/select-start
```typescript
await apiClient.selectStart(imageId, x, y)
// Returns: { valid, coordinates, message }
```

### 3. POST /api/select-goal
```typescript
await apiClient.selectGoal(imageId, x, y)
// Returns: { valid, coordinates, path, message }
```

### 4. POST /api/clear-selection
```typescript
await apiClient.clearSelection(imageId)
// Returns: { message }
```

### 5. GET /api/state/{image_id}
```typescript
await apiClient.getState(imageId)
// Returns: { image_id, has_image, start_point, goal_point, path }
```

## Setup Instructions

### 1. Navigate to Frontend Directory
```bash
cd v0-road-mapping-interface-main/v0-road-mapping-interface-main
```

### 2. Install Dependencies
```bash
npm install
# or
pnpm install
# or
yarn install
```

### 3. Start Development Server
```bash
npm run dev
# or
pnpm dev
# or
yarn dev
```

The frontend will start on `http://localhost:3000`

### 4. Start Backend Server
In a separate terminal, start your Python backend:
```bash
python run_server.py
```

The backend should be running on `http://localhost:5000`

## Configuration

### Backend API URL

The API client is configured to connect to `http://localhost:5000/api` by default.

To change the backend URL, modify `lib/api-client.ts`:

```typescript
const DEFAULT_BASE_URL = 'http://localhost:5000/api'
// Change to your backend URL if different
```

### CORS Configuration

Your backend already has CORS enabled in `src/api/app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],  # Frontend URL
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

## Testing the Integration

### 1. Start Both Servers
- Backend: `python run_server.py` (port 5000)
- Frontend: `npm run dev` (port 3000)

### 2. Open Browser
Navigate to `http://localhost:3000`

### 3. Test Workflow
1. Click "Upload Image" and select a satellite image
2. Wait for processing (road segmentation + graph construction)
3. Click on a road pixel to set start point (green marker)
4. Click on another road pixel to set goal point (red marker)
5. Path should appear automatically (blue line)
6. Use "Clear Selection" to reset and try again

### 4. Test Error Scenarios
- Upload invalid image → should show error notification
- Click off-road pixel → should show "Please click on a road" error
- Test with disconnected backend → should show connection error

## Component Details

### MapCanvas Component
- **Layered Canvas Architecture:** Uses 4 separate canvas layers for optimal performance
  - Layer 1: Base satellite image
  - Layer 2: Road mask overlay
  - Layer 3: Path visualization
  - Layer 4: Markers (start/goal)
- **Coordinate Conversion:** Properly converts screen clicks to image coordinates
- **Responsive:** Handles different image sizes and aspect ratios

### ControlsPanel Component
- **File Upload:** Drag-and-drop or click to upload
- **Point Status:** Visual indicators for start/goal selection
- **Overlay Controls:** Toggle visibility and adjust opacity
- **Instructions:** Built-in user guide

### Notifications Component
- **Toast System:** Non-blocking notifications
- **Auto-dismiss:** Success messages auto-dismiss after 5 seconds
- **Manual Dismiss:** Error messages require user acknowledgment
- **Loading States:** Spinner for long operations

## Performance Optimizations

✅ **Layered Canvas Rendering**
- Only redraws changed layers
- Reduces unnecessary re-renders

✅ **Debounced Click Events**
- Prevents double-click issues
- Improves user experience

✅ **Lazy Loading**
- Components load on demand
- Faster initial page load

✅ **Image Optimization**
- Base64 encoding for efficient transfer
- Canvas-based rendering for performance

## Troubleshooting

### Issue: "Failed to load image"
**Solution:** Check that backend is running on port 5000 and CORS is enabled

### Issue: "Please click on a road" always appears
**Solution:** Verify road segmentation is working correctly in backend

### Issue: Path not displaying
**Solution:** Check browser console for errors, verify path data format

### Issue: Canvas not responding to clicks
**Solution:** Check coordinate conversion logic, verify canvas dimensions

### Issue: CORS errors in browser console
**Solution:** Verify CORS configuration in backend matches frontend URL

## Production Deployment

### Frontend Deployment
```bash
npm run build
npm start
```

Or deploy to Vercel/Netlify/etc.

### Backend Deployment
Deploy your Python backend to a cloud service (AWS, GCP, Heroku, etc.)

### Update API URL
Change `DEFAULT_BASE_URL` in `lib/api-client.ts` to your production backend URL

### Environment Variables
Create `.env.local` for environment-specific configuration:
```
NEXT_PUBLIC_API_URL=https://your-backend-api.com/api
```

## Next Steps

1. ✅ Frontend is ready to use
2. ✅ Backend API is fully implemented
3. ✅ Integration is complete

### Optional Enhancements
- Add zoom/pan functionality for large images
- Add path distance/cost display
- Add multiple waypoint support
- Add image history/session management
- Add keyboard shortcuts
- Add accessibility improvements (ARIA labels, keyboard navigation)

## Support

If you encounter any issues:
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify both servers are running
4. Test API endpoints directly with curl/Postman
5. Check CORS configuration

## Summary

The frontend is a production-ready Next.js application that seamlessly integrates with your Python backend. It implements all required features from the spec:
- Image loading and display
- Road segmentation visualization
- Interactive point selection
- Pathfinding visualization
- Error handling and user feedback
- Responsive design

Simply start both servers and navigate to `http://localhost:3000` to begin using the interactive road mapping interface!
