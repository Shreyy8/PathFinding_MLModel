# UI Agent Prompt: Interactive Road Mapping Interface Frontend

## Mission

Build a web-based frontend interface (HTML/CSS/JavaScript) for an interactive road mapping and pathfinding system. The UI will communicate with a Python backend via REST API to display satellite images, visualize road networks, handle user point selection, and display computed shortest paths.

## Backend API Contract

The backend exposes a REST API at `http://localhost:5000/api` with the following endpoints:

### 1. POST /api/load-image
Upload and process a satellite image.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` (file upload)

**Response (Success - 200):**
```json
{
  "image_id": "uuid-string",
  "image_data": "base64-encoded-image",
  "road_mask_data": "base64-encoded-mask",
  "width": 1024,
  "height": 768,
  "message": "Image processed successfully"
}
```

**Response (Error - 400/500):**
```json
{
  "error": "Error message description",
  "details": "Additional error details",
  "code": "ERROR_CODE"
}
```

---

### 2. POST /api/select-start
Select a start point for pathfinding.

**Request:**
```json
{
  "image_id": "uuid-string",
  "x": 512,
  "y": 384
}
```

**Response (Valid Point - 200):**
```json
{
  "valid": true,
  "coordinates": {"x": 512, "y": 384},
  "message": "Start point selected"
}
```

**Response (Invalid Point - 400):**
```json
{
  "valid": false,
  "error": "Point is not on a road",
  "coordinates": {"x": 512, "y": 384}
}
```

---

### 3. POST /api/select-goal
Select a goal point and compute path.

**Request:**
```json
{
  "image_id": "uuid-string",
  "x": 256,
  "y": 192
}
```

**Response (Valid Point with Path - 200):**
```json
{
  "valid": true,
  "coordinates": {"x": 256, "y": 192},
  "path": [[512, 384], [500, 380], [256, 192]],
  "message": "Goal point selected and path computed"
}
```

**Response (Valid Point without Start - 200):**
```json
{
  "valid": true,
  "coordinates": {"x": 256, "y": 192},
  "path": null,
  "message": "Goal point selected (no start point yet)"
}
```

---

### 4. POST /api/clear-selection
Clear start and goal points.

**Request:**
```json
{
  "image_id": "uuid-string"
}
```

**Response (200):**
```json
{
  "message": "Selection cleared"
}
```

---

### 5. GET /api/state/{image_id}
Retrieve current state.

**Response (200):**
```json
{
  "image_id": "uuid-string",
  "has_image": true,
  "start_point": {"x": 512, "y": 384},
  "goal_point": {"x": 256, "y": 192},
  "path": [[512, 384], [500, 380], [256, 192]]
}
```

---

## Coordinate System

- **Origin:** Top-left corner (0, 0)
- **X-axis:** Increases to the right
- **Y-axis:** Increases downward
- **Units:** Pixels in image space

---

## Required UI Components

You need to build 7 main components:

### Component 1: ImageDisplay
**Purpose:** Display the satellite image in the browser

**Responsibilities:**
- Render uploaded satellite image
- Maintain aspect ratio
- Handle image loading states
- Provide canvas or image element for overlays
- Convert click events to image coordinates

**Interface:**
```javascript
class ImageDisplay {
  constructor(containerId)
  loadImage(imageData)  // imageData: base64 string
  getImageDimensions()  // returns {width, height}
  getClickCoordinates(event)  // converts click to image coordinates
}
```

**Implementation Notes:**
- Use HTML5 Canvas for precise coordinate mapping
- Handle image scaling if displayed size differs from actual size
- Ensure click coordinates are in image space, not screen space

---

### Component 2: OverlayRenderer
**Purpose:** Render road mask overlay on top of satellite image

**Responsibilities:**
- Display road mask with transparency
- Blend overlay with base image
- Update overlay when new mask data received
- Use configurable opacity (default: 0.5)

**Interface:**
```javascript
class OverlayRenderer {
  constructor(imageDisplay)
  setRoadMask(maskData)  // maskData: base64 string
  setOpacity(opacity)  // opacity: 0.0 to 1.0
  show()
  hide()
}
```

**Implementation Notes:**
- Use Canvas globalAlpha or CSS opacity for transparency
- Ensure road pixels are visually distinct (e.g., red or yellow overlay)
- Preserve visibility of underlying satellite image

---

### Component 3: ClickHandler
**Purpose:** Capture and process user click events on the map

**Responsibilities:**
- Listen for click events on image
- Convert screen coordinates to image coordinates
- Determine if click is for start or goal point
- Send coordinates to backend API
- Handle API responses

**Interface:**
```javascript
class ClickHandler {
  constructor(imageDisplay, apiClient)
  enableStartSelection()
  enableGoalSelection()
  disable()
  onPointSelected(callback)  // callback(pointType, coordinates, valid)
}
```

**Implementation Notes:**
- Implement state machine: idle → selecting start → selecting goal
- Debounce clicks to prevent double-selection
- Provide visual feedback during API request (loading cursor)

---

### Component 4: MarkerVisualizer
**Purpose:** Display start and goal point markers on the map

**Responsibilities:**
- Render start marker (e.g., green circle with "S")
- Render goal marker (e.g., red circle with "G")
- Update marker positions
- Clear markers

**Interface:**
```javascript
class MarkerVisualizer {
  constructor(imageDisplay)
  setStartMarker(x, y)
  setGoalMarker(x, y)
  clearStartMarker()
  clearGoalMarker()
  clearAllMarkers()
}
```

**Implementation Notes:**
- Use distinct colors: green for start, red for goal
- Make markers large enough to be visible (e.g., 20px radius)
- Consider adding labels ("S" and "G") inside markers
- Ensure markers are drawn on top of all other layers

---

### Component 5: PathVisualizer
**Purpose:** Display computed shortest path on the map

**Responsibilities:**
- Render path as polyline
- Style path (color, width, opacity)
- Update path when recomputed
- Clear path

**Interface:**
```javascript
class PathVisualizer {
  constructor(imageDisplay)
  setPath(pathCoordinates)  // pathCoordinates: [[x1,y1], [x2,y2], ...]
  setStyle(color, width, opacity)
  clearPath()
}
```

**Implementation Notes:**
- Use Canvas lineTo() or SVG polyline for path rendering
- Use visually distinct color (e.g., blue or cyan)
- Use appropriate line width (e.g., 3-5px)
- Draw path on top of road overlay but below markers

---

### Component 6: NotificationSystem
**Purpose:** Display messages, errors, and status updates to user

**Responsibilities:**
- Show success messages
- Show error messages
- Show loading indicators
- Auto-dismiss or require user acknowledgment

**Interface:**
```javascript
class NotificationSystem {
  constructor(containerId)
  showSuccess(message)
  showError(message)
  showInfo(message)
  showLoading(message)
  hideLoading()
  clear()
}
```

**Implementation Notes:**
- Use toast notifications or modal dialogs
- Color-code messages: green for success, red for error, blue for info
- Auto-dismiss success messages after 3-5 seconds
- Keep error messages visible until user dismisses
- Show loading spinner during API requests

---

### Component 7: APIClient
**Purpose:** Handle all HTTP communication with backend

**Responsibilities:**
- Make API requests
- Handle responses and errors
- Parse JSON data
- Manage request state

**Interface:**
```javascript
class APIClient {
  constructor(baseUrl)
  async loadImage(imageFile)
  async selectStart(imageId, x, y)
  async selectGoal(imageId, x, y)
  async clearSelection(imageId)
  async getState(imageId)
}
```

**Implementation Notes:**
- Use Fetch API or Axios for HTTP requests
- Handle network errors gracefully
- Parse error responses and extract error messages
- Set appropriate headers (Content-Type, etc.)

---

## Complete UI Workflow

1. **User uploads image** via file input
2. **ImageDisplay** shows loading state
3. **APIClient** sends image to `POST /api/load-image`
4. **Backend** processes and returns `image_id`, `image_data`, `road_mask_data`
5. **ImageDisplay** renders satellite image
6. **OverlayRenderer** renders road mask overlay
7. **ClickHandler** enables start point selection
8. **User clicks on map**
9. **ClickHandler** converts click to coordinates, sends to `POST /api/select-start`
10. **Backend** validates point, returns result
11. **If valid:** **MarkerVisualizer** displays start marker, **ClickHandler** enables goal selection
12. **If invalid:** **NotificationSystem** shows error message
13. **User clicks goal point**
14. **ClickHandler** sends to `POST /api/select-goal`
15. **Backend** validates, computes path, returns result
16. **MarkerVisualizer** displays goal marker
17. **PathVisualizer** displays computed path

---

## UI Layout Recommendations

```html
<!DOCTYPE html>
<html>
<head>
  <title>Interactive Road Mapping</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f0f0f0;
    }
    #container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    #controls {
      margin-bottom: 20px;
    }
    #map-container {
      position: relative;
      border: 2px solid #ccc;
      display: inline-block;
    }
    #canvas {
      display: block;
      cursor: crosshair;
    }
    #notifications {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 1000;
    }
    .notification {
      padding: 15px;
      margin-bottom: 10px;
      border-radius: 4px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .notification.success {
      background: #4caf50;
      color: white;
    }
    .notification.error {
      background: #f44336;
      color: white;
    }
    .notification.info {
      background: #2196f3;
      color: white;
    }
  </style>
</head>
<body>
  <div id="container">
    <h1>Interactive Road Mapping Interface</h1>
    
    <div id="controls">
      <input type="file" id="image-upload" accept="image/*">
      <button id="clear-btn" disabled>Clear Selection</button>
      <span id="status">Upload an image to begin</span>
    </div>
    
    <div id="map-container">
      <canvas id="canvas"></canvas>
    </div>
  </div>
  
  <div id="notifications"></div>
  
  <script src="api-client.js"></script>
  <script src="image-display.js"></script>
  <script src="overlay-renderer.js"></script>
  <script src="click-handler.js"></script>
  <script src="marker-visualizer.js"></script>
  <script src="path-visualizer.js"></script>
  <script src="notification-system.js"></script>
  <script src="main.js"></script>
</body>
</html>
```

---

## Error Handling Requirements

1. **Network Errors:** Show "Connection failed" message with retry option
2. **Invalid Image:** Show "Invalid image file" message
3. **Segmentation Failure:** Show "Road detection failed" with retry option
4. **Invalid Point Selection:** Show "Please click on a road" message
5. **Pathfinding Failure:** Show "No path found between points" message
6. **Loading States:** Show spinner during API requests
7. **Timeout:** Handle requests that take too long (>30 seconds)

---

## Visual Design Guidelines

### Colors
- **Start Marker:** Green (#4caf50)
- **Goal Marker:** Red (#f44336)
- **Path:** Blue (#2196f3)
- **Road Overlay:** Red or Yellow with 50% opacity
- **Background:** Light gray (#f0f0f0)

### Sizes
- **Markers:** 20px radius circles
- **Path Line:** 4px width
- **Canvas Border:** 2px solid #ccc

### Typography
- **Font:** Arial, sans-serif
- **Headings:** 24px, bold
- **Body:** 14px, normal
- **Status Text:** 12px, italic

---

## Testing Recommendations

### Unit Testing
Test each component independently:

1. **ImageDisplay Tests:**
   - Test image loading with valid base64 data
   - Test coordinate conversion from screen to image space
   - Test handling of different image aspect ratios
   - Test canvas resizing on window resize

2. **OverlayRenderer Tests:**
   - Test mask overlay rendering with various opacity values
   - Test show/hide functionality
   - Test overlay alignment with base image

3. **ClickHandler Tests:**
   - Test click coordinate capture and conversion
   - Test state transitions (idle → start → goal)
   - Test debouncing of rapid clicks
   - Test API call triggering on valid clicks

4. **MarkerVisualizer Tests:**
   - Test marker rendering at correct coordinates
   - Test marker clearing functionality
   - Test marker visibility on various backgrounds

5. **PathVisualizer Tests:**
   - Test path rendering with various coordinate arrays
   - Test path clearing functionality
   - Test path styling (color, width, opacity)

6. **NotificationSystem Tests:**
   - Test success/error/info message display
   - Test auto-dismiss timing for success messages
   - Test manual dismiss for error messages
   - Test loading indicator show/hide

7. **APIClient Tests:**
   - Test successful API calls with mock responses
   - Test error handling for network failures
   - Test error handling for 400/500 responses
   - Test request timeout handling

### Integration Testing
Test component interactions:

1. **Complete Workflow Test:**
   - Upload image → verify display and overlay
   - Select start point → verify marker display
   - Select goal point → verify marker and path display
   - Clear selection → verify all markers and path removed

2. **Error Scenario Tests:**
   - Upload invalid image → verify error message
   - Click off-road point → verify rejection message
   - Simulate network failure → verify error handling
   - Simulate backend error → verify error display

3. **Point Reselection Tests:**
   - Select start, then select new start → verify old marker cleared
   - Select both points, then change start → verify path recomputed
   - Select both points, then change goal → verify path recomputed

### Browser Compatibility Testing
Test on multiple browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Responsive Design Testing
Test on various screen sizes:
- Desktop (1920x1080, 1366x768)
- Tablet (768x1024)
- Mobile (375x667, 414x896)

### Performance Testing
1. Test with large images (2048x2048 pixels)
2. Test with complex paths (100+ waypoints)
3. Measure rendering time for overlays and paths
4. Test memory usage during extended sessions

---

## Technology Stack Recommendations

- **HTML5 Canvas** for image display and overlays (precise coordinate control)
- **Vanilla JavaScript** or lightweight framework (React, Vue) for component logic
- **Fetch API** or Axios for HTTP requests
- **CSS3** for styling and animations
- **No external dependencies** for core functionality (optional: Bootstrap for UI styling)

---

## Performance Considerations

1. **Image Optimization:** Resize large images before upload (max 2048x2048)
2. **Canvas Rendering:** Use requestAnimationFrame for smooth animations
3. **Debouncing:** Debounce click events (100ms) to prevent double-clicks
4. **Caching:** Cache image_id in sessionStorage to persist across page refreshes
5. **Lazy Loading:** Load components only when needed
6. **Memory Management:** Clear canvas and release resources when loading new images
7. **Efficient Redrawing:** Only redraw changed layers (use layered canvases if needed)
8. **Throttling:** Throttle resize events to avoid excessive redraws

### Example: Layered Canvas Approach
For better performance, consider using multiple canvas layers:
- **Layer 1 (bottom):** Satellite image (rarely changes)
- **Layer 2:** Road overlay (rarely changes)
- **Layer 3:** Path visualization (changes on reselection)
- **Layer 4 (top):** Markers (changes frequently)

This allows redrawing only the layers that change, improving performance.

---

## Implementation Examples

### Example 1: ImageDisplay Component

```javascript
class ImageDisplay {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.container.appendChild(this.canvas);
    this.image = null;
    this.scale = 1;
  }

  loadImage(imageData) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.image = img;
        this.canvas.width = img.width;
        this.canvas.height = img.height;
        this.ctx.drawImage(img, 0, 0);
        resolve();
      };
      img.onerror = reject;
      img.src = `data:image/png;base64,${imageData}`;
    });
  }

  getImageDimensions() {
    return {
      width: this.canvas.width,
      height: this.canvas.height
    };
  }

  getClickCoordinates(event) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    
    return {
      x: Math.floor((event.clientX - rect.left) * scaleX),
      y: Math.floor((event.clientY - rect.top) * scaleY)
    };
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}
```

### Example 2: APIClient Component

```javascript
class APIClient {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
  }

  async loadImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${this.baseUrl}/load-image`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to load image');
    }

    return await response.json();
  }

  async selectStart(imageId, x, y) {
    const response = await fetch(`${this.baseUrl}/select-start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_id: imageId, x, y })
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to select start point');
    }

    return data;
  }

  async selectGoal(imageId, x, y) {
    const response = await fetch(`${this.baseUrl}/select-goal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_id: imageId, x, y })
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Failed to select goal point');
    }

    return data;
  }

  async clearSelection(imageId) {
    const response = await fetch(`${this.baseUrl}/clear-selection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_id: imageId })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to clear selection');
    }

    return await response.json();
  }

  async getState(imageId) {
    const response = await fetch(`${this.baseUrl}/state/${imageId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to get state');
    }

    return await response.json();
  }
}
```

### Example 3: MarkerVisualizer Component

```javascript
class MarkerVisualizer {
  constructor(imageDisplay) {
    this.canvas = imageDisplay.canvas;
    this.ctx = imageDisplay.ctx;
    this.startMarker = null;
    this.goalMarker = null;
  }

  setStartMarker(x, y) {
    this.startMarker = { x, y };
    this.drawMarker(x, y, '#4caf50', 'S');
  }

  setGoalMarker(x, y) {
    this.goalMarker = { x, y };
    this.drawMarker(x, y, '#f44336', 'G');
  }

  drawMarker(x, y, color, label) {
    const radius = 20;
    
    // Draw circle
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
    this.ctx.fillStyle = color;
    this.ctx.fill();
    this.ctx.strokeStyle = 'white';
    this.ctx.lineWidth = 3;
    this.ctx.stroke();
    
    // Draw label
    this.ctx.fillStyle = 'white';
    this.ctx.font = 'bold 16px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.textBaseline = 'middle';
    this.ctx.fillText(label, x, y);
  }

  clearStartMarker() {
    this.startMarker = null;
  }

  clearGoalMarker() {
    this.goalMarker = null;
  }

  clearAllMarkers() {
    this.startMarker = null;
    this.goalMarker = null;
  }

  redraw() {
    if (this.startMarker) {
      this.drawMarker(this.startMarker.x, this.startMarker.y, '#4caf50', 'S');
    }
    if (this.goalMarker) {
      this.drawMarker(this.goalMarker.x, this.goalMarker.y, '#f44336', 'G');
    }
  }
}
```

### Example 4: Main Application Integration

```javascript
// main.js
document.addEventListener('DOMContentLoaded', () => {
  // Initialize components
  const apiClient = new APIClient();
  const imageDisplay = new ImageDisplay('map-container');
  const overlayRenderer = new OverlayRenderer(imageDisplay);
  const markerVisualizer = new MarkerVisualizer(imageDisplay);
  const pathVisualizer = new PathVisualizer(imageDisplay);
  const notificationSystem = new NotificationSystem('notifications');
  const clickHandler = new ClickHandler(imageDisplay, apiClient);

  let currentImageId = null;
  let selectionMode = 'none'; // 'none', 'start', 'goal'

  // File upload handler
  document.getElementById('image-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      notificationSystem.showLoading('Processing image...');
      
      const response = await apiClient.loadImage(file);
      currentImageId = response.image_id;
      
      await imageDisplay.loadImage(response.image_data);
      overlayRenderer.setRoadMask(response.road_mask_data);
      overlayRenderer.show();
      
      notificationSystem.hideLoading();
      notificationSystem.showSuccess('Image loaded successfully. Click to select start point.');
      
      selectionMode = 'start';
      document.getElementById('clear-btn').disabled = false;
      
    } catch (error) {
      notificationSystem.hideLoading();
      notificationSystem.showError(`Failed to load image: ${error.message}`);
    }
  });

  // Canvas click handler
  imageDisplay.canvas.addEventListener('click', async (e) => {
    if (!currentImageId || selectionMode === 'none') return;

    const coords = imageDisplay.getClickCoordinates(e);

    try {
      if (selectionMode === 'start') {
        const response = await apiClient.selectStart(currentImageId, coords.x, coords.y);
        
        if (response.valid) {
          markerVisualizer.setStartMarker(coords.x, coords.y);
          notificationSystem.showSuccess('Start point selected. Click to select goal point.');
          selectionMode = 'goal';
        } else {
          notificationSystem.showError('Please click on a road');
        }
        
      } else if (selectionMode === 'goal') {
        const response = await apiClient.selectGoal(currentImageId, coords.x, coords.y);
        
        if (response.valid) {
          markerVisualizer.setGoalMarker(coords.x, coords.y);
          
          if (response.path) {
            pathVisualizer.setPath(response.path);
            notificationSystem.showSuccess('Path computed successfully!');
          } else {
            notificationSystem.showInfo('Goal point selected. Select start point to compute path.');
          }
        } else {
          notificationSystem.showError('Please click on a road');
        }
      }
      
    } catch (error) {
      notificationSystem.showError(`Error: ${error.message}`);
    }
  });

  // Clear button handler
  document.getElementById('clear-btn').addEventListener('click', async () => {
    if (!currentImageId) return;

    try {
      await apiClient.clearSelection(currentImageId);
      
      markerVisualizer.clearAllMarkers();
      pathVisualizer.clearPath();
      
      // Redraw base image and overlay
      await imageDisplay.loadImage(/* cached image data */);
      overlayRenderer.show();
      
      selectionMode = 'start';
      notificationSystem.showInfo('Selection cleared. Click to select start point.');
      
    } catch (error) {
      notificationSystem.showError(`Failed to clear selection: ${error.message}`);
    }
  });
});
```

---

## Deliverables

Please provide:

1. **HTML file** with complete UI structure
2. **JavaScript files** for each component (7 files)
3. **CSS file** for styling
4. **README** with setup instructions
5. **Demo** showing the complete workflow

---

## Success Criteria

The UI is complete when:

1. ✅ User can upload a satellite image
2. ✅ Road overlay displays correctly with transparency
3. ✅ User can click to select start point (with validation)
4. ✅ User can click to select goal point (with validation)
5. ✅ Start and goal markers display correctly
6. ✅ Computed path displays as a colored line
7. ✅ Error messages display for invalid actions
8. ✅ User can clear selection and start over
9. ✅ All API endpoints are called correctly
10. ✅ UI is responsive and works on different screen sizes

---

## Additional Notes

- The backend API will be running on `http://localhost:5000`
- CORS is enabled on the backend for browser access
- Image data is transmitted as base64-encoded strings
- All coordinates are in pixel space relative to the original image
- The UI should handle images of varying sizes and aspect ratios
- Consider adding zoom/pan functionality for large images (optional enhancement)
- Consider adding a legend explaining the colors and markers (optional enhancement)

### Common Error Codes from Backend

The backend returns specific error codes that you should handle:

- `INVALID_IMAGE`: Image format or size invalid
- `SEGMENTATION_FAILED`: Road segmentation failed
- `GRAPH_CONSTRUCTION_FAILED`: Graph construction failed
- `POINT_NOT_ON_ROAD`: Selected point not on road
- `PATHFINDING_FAILED`: Path computation failed
- `IMAGE_NOT_FOUND`: Invalid image_id
- `INVALID_COORDINATES`: Coordinates out of bounds

### State Management Best Practices

1. **Cache image_id:** Store in sessionStorage to persist across page refreshes
2. **Cache image data:** Store base64 image data to avoid re-fetching
3. **Track selection state:** Maintain state machine (idle → start → goal)
4. **Handle page refresh:** Restore state from sessionStorage if available
5. **Clean up on new image:** Clear all markers, paths, and cached data

### Accessibility Considerations

1. **Keyboard Navigation:** Add keyboard shortcuts for common actions
2. **Screen Reader Support:** Add ARIA labels to interactive elements
3. **Focus Management:** Ensure proper focus order and visibility
4. **Color Contrast:** Ensure sufficient contrast for markers and paths
5. **Alternative Text:** Provide alt text for images and visual elements

### Security Considerations

1. **Input Validation:** Validate file types and sizes before upload
2. **XSS Prevention:** Sanitize any user-generated content
3. **CORS:** Backend has CORS enabled, but be aware of security implications
4. **File Size Limits:** Enforce maximum file size (e.g., 10MB)
5. **Content-Type Validation:** Verify uploaded files are valid images

---

## Questions?

If you need clarification on any aspect of the API contract, component specifications, or workflow, please ask before starting implementation.

Good luck building the UI! 🚀
