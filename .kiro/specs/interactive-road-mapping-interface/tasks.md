# Implementation Plan: Interactive Road Mapping Interface

## Overview

This implementation plan creates a Python backend API that integrates with existing components (RoadSegmentationModel, GraphConstructor, PathfindingEngine) and exposes REST endpoints for a web-based UI. The backend handles image processing, road segmentation, graph construction, point validation, and pathfinding. The frontend UI (HTML/CSS/JavaScript) will be built by an external agent based on the API contract defined in the design document.

## Tasks

- [x] 1. Set up Flask/FastAPI backend structure
  - Create directory structure for the backend API module
  - Set up Flask or FastAPI application with CORS support
  - Define configuration for API settings (host, port, CORS origins)
  - Create base exception classes for API error handling
  - Set up logging configuration
  - _Requirements: 10.1, 10.2, 10.3, 11.3_

- [x] 2. Implement StateManager component
  - [x] 2.1 Create StateManager class with session storage
    - Implement in-memory dictionary to store sessions by image_id
    - Create methods to store image, road_mask, road_graph per session
    - Implement methods to store start_point, goal_point, and path
    - Add session existence check and retrieval methods
    - _Requirements: 1.1, 5.3, 6.3, 9.1_
  
  - [x] 2.2 Implement state update and clearing methods
    - Create set_start_point, set_goal_point, set_path methods
    - Implement clear_selection method to reset points and path
    - Add validation to ensure session exists before updates
    - _Requirements: 5.3, 6.3, 9.1, 9.2_
  
  - [x] 2.3 Write unit tests for StateManager
    - Test session creation and retrieval
    - Test state updates and clearing
    - Test error handling for invalid session_id
    - _Requirements: 1.1, 5.3, 6.3, 9.1_

- [x] 3. Implement PointValidator component
  - [x] 3.1 Create PointValidator class with validation logic
    - Implement validate_point method to check coordinates against road mask
    - Check if coordinates are within image bounds
    - Check if coordinates correspond to road pixel (mask value > 0)
    - Return boolean validation result
    - _Requirements: 5.2, 6.2_
  
  - [x] 3.2 Write property test for PointValidator
    - **Property 6: Point Validation**
    - **Property 7: Valid Point Acceptance**
    - **Property 8: Invalid Point Rejection**
    - **Validates: Requirements 5.2, 5.3, 5.4, 6.2, 6.3, 6.4**

- [x] 4. Implement ImageProcessor component
  - [x] 4.1 Create ImageProcessor class with image handling methods
    - Implement load_image to convert uploaded file bytes to numpy array
    - Implement validate_image to check format and size
    - Implement encode_image_to_base64 for API responses
    - Implement encode_mask_to_base64 with transparency overlay
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 4.2 Write property test for ImageProcessor
    - **Property 1: Image Display Preservation**
    - **Property 2: Invalid Image Rejection**
    - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 5. Implement PathfindingCoordinator component
  - [x] 5.1 Create PathfindingCoordinator class
    - Initialize with PathfindingEngine instance
    - Implement compute_path method that invokes PathfindingEngine
    - Convert path result to list of (x, y) coordinate tuples
    - Handle pathfinding errors and raise appropriate exceptions
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 10.3_
  
  - [x] 5.2 Write property test for PathfindingCoordinator
    - **Property 11: Pathfinding Invocation**
    - **Validates: Requirements 7.1, 7.2**

- [x] 6. Checkpoint - Ensure component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement POST /api/load-image endpoint
  - [x] 7.1 Create load_image route handler
    - Accept multipart/form-data file upload
    - Generate unique image_id using UUID
    - Use ImageProcessor to load and validate image
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 7.2 Integrate RoadSegmentationModel in load_image handler
    - Invoke RoadSegmentationModel.segment(image) to generate road_mask
    - Handle segmentation errors with try-except and return 500 error
    - _Requirements: 2.1, 2.2, 2.3, 10.1_
  
  - [x] 7.3 Integrate GraphConstructor in load_image handler
    - Invoke GraphConstructor.build_graph(road_mask) to generate road_graph
    - Handle graph construction errors with try-except and return 500 error
    - _Requirements: 4.1, 4.2, 4.3, 10.2_
  
  - [x] 7.4 Complete load_image handler with state storage and response
    - Store image, road_mask, road_graph in StateManager with image_id
    - Encode image and mask to base64 using ImageProcessor
    - Return JSON response with image_id, image_data, road_mask_data, width, height
    - _Requirements: 1.1, 2.2, 4.2_
  
  - [x] 7.5 Write property tests for load_image endpoint
    - **Property 3: Segmentation Invocation**
    - **Property 5: Graph Construction Trigger**
    - **Property 18: API Response Format Consistency**
    - **Validates: Requirements 2.1, 2.2, 4.1, 4.2**

- [x] 8. Implement POST /api/select-start endpoint
  - [x] 8.1 Create select_start route handler
    - Accept JSON request with image_id, x, y coordinates
    - Validate that session exists for image_id
    - Retrieve road_mask from StateManager
    - _Requirements: 5.1, 5.2_
  
  - [x] 8.2 Add point validation to select_start handler
    - Use PointValidator to validate coordinates against road_mask
    - If invalid: return 400 error with {valid: false, error: "Point is not on a road"}
    - If valid: update StateManager with start_point
    - Clear any existing path from StateManager
    - _Requirements: 5.2, 5.3, 5.4, 9.2_
  
  - [x] 8.3 Complete select_start handler with response
    - Return JSON response with {valid: true, coordinates: {x, y}, message}
    - _Requirements: 5.3_
  
  - [x] 8.4 Write property tests for select_start endpoint
    - **Property 7: Valid Point Acceptance**
    - **Property 8: Invalid Point Rejection**
    - **Property 19: State Consistency**
    - **Validates: Requirements 5.2, 5.3, 5.4**

- [x] 9. Implement POST /api/select-goal endpoint
  - [x] 9.1 Create select_goal route handler
    - Accept JSON request with image_id, x, y coordinates
    - Validate that session exists for image_id
    - Retrieve road_mask from StateManager
    - Use PointValidator to validate coordinates
    - _Requirements: 6.1, 6.2_
  
  - [x] 9.2 Add pathfinding logic to select_goal handler
    - If point is invalid: return 400 error with {valid: false, error: "Point is not on a road"}
    - If point is valid: update StateManager with goal_point
    - Check if start_point exists in StateManager
    - If both start and goal exist: invoke PathfindingCoordinator to compute path
    - _Requirements: 6.2, 6.3, 6.4, 7.1, 7.2_
  
  - [x] 9.3 Handle pathfinding results and errors
    - If pathfinding succeeds: store path in StateManager
    - If pathfinding fails (no path): return 400 error with appropriate message
    - If pathfinding raises exception: return 500 error
    - _Requirements: 7.2, 7.3, 7.4, 11.1_
  
  - [x] 9.4 Complete select_goal handler with response
    - Return JSON with {valid: true, coordinates: {x, y}, path: [...], message}
    - If no start point: return {valid: true, coordinates: {x, y}, path: null, message}
    - _Requirements: 6.3, 7.2_
  
  - [x] 9.5 Write property tests for select_goal endpoint
    - **Property 11: Pathfinding Invocation**
    - **Property 13: Point Reselection and Path Clearing**
    - **Validates: Requirements 6.2, 6.3, 7.1, 7.2, 9.1, 9.2, 9.3**

- [x] 10. Implement POST /api/clear-selection endpoint
  - [x] 10.1 Create clear_selection route handler
    - Accept JSON request with image_id
    - Validate that session exists
    - Use StateManager.clear_selection to reset start, goal, and path
    - Return JSON response with {message: "Selection cleared"}
    - _Requirements: 9.1, 9.2_
  
  - [x] 10.2 Write unit tests for clear_selection endpoint
    - Test successful clearing
    - Test error handling for invalid image_id
    - _Requirements: 9.1, 9.2_

- [x] 11. Implement GET /api/state/{image_id} endpoint
  - [x] 11.1 Create get_state route handler
    - Accept image_id as URL parameter
    - Validate that session exists
    - Retrieve current state from StateManager
    - Return JSON with {image_id, has_image, start_point, goal_point, path}
    - Handle missing session with 404 error
    - _Requirements: 1.1, 5.3, 6.3, 7.2_
  
  - [x] 11.2 Write property test for get_state endpoint
    - **Property 19: State Consistency**
    - **Validates: State Management**

- [x] 12. Checkpoint - Ensure API endpoint tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Implement comprehensive error handling and logging
  - [x] 13.1 Create centralized error handler
    - Implement Flask/FastAPI error handlers for common exceptions
    - Map exceptions to appropriate HTTP status codes
    - Format error responses with {error, details, code} structure
    - _Requirements: 11.1, 11.3_
  
  - [x] 13.2 Add error logging throughout API
    - Log all errors with timestamp, error type, and stack trace
    - Log API requests and responses for debugging
    - Use appropriate log levels (ERROR, WARNING, INFO)
    - _Requirements: 11.3_
  
  - [x] 13.3 Implement error codes for common failures
    - Define error codes: INVALID_IMAGE, SEGMENTATION_FAILED, GRAPH_CONSTRUCTION_FAILED, POINT_NOT_ON_ROAD, PATHFINDING_FAILED, IMAGE_NOT_FOUND, INVALID_COORDINATES
    - Return error codes in API error responses
    - _Requirements: 11.1, 11.2_
  
  - [x] 13.4 Write property tests for error handling
    - **Property 14: Component Failure Error Handling**
    - **Property 16: Error Logging**
    - **Property 17: Recoverable Error Retry**
    - **Validates: Requirements 2.3, 4.3, 7.4, 11.1, 11.2, 11.3, 11.4**

- [x] 14. Wire all components together and create main application
  - [x] 14.1 Create main application entry point
    - Initialize RoadSegmentationModel, GraphConstructor, PathfindingEngine
    - Initialize StateManager, PointValidator, ImageProcessor, PathfindingCoordinator
    - Initialize BackendAPI with all components
    - Configure CORS for browser access
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 14.2 Add application configuration
    - Set up configuration for host, port, debug mode
    - Configure CORS origins for development and production
    - Add configuration for image size limits and session timeout
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 14.3 Create run script for backend server
    - Create script to start Flask/FastAPI server
    - Add command-line arguments for configuration overrides
    - Document how to run the server
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 14.4 Write integration tests for complete backend workflow
    - Test full workflow: load image → select start → select goal → get path
    - Test error scenarios and recovery paths
    - Test point reselection and path recomputation
    - Test state retrieval and consistency
    - _Requirements: 1.1, 2.1, 4.1, 5.1, 6.1, 7.1, 9.1, 9.2, 9.3_

- [x] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Generate detailed UI agent prompt
  - [x] 16.1 Create comprehensive prompt for external UI agent
    - Reference the API contract section from design.md
    - Reference the Frontend UI Components section from design.md
    - Specify that UI should be built with HTML/CSS/JavaScript
    - List all required UI components: ImageDisplay, OverlayRenderer, ClickHandler, MarkerVisualizer, PathVisualizer, NotificationSystem, APIClient
    - Provide detailed specifications for each component's responsibilities and interface
    - Include the complete UI workflow from design.md
    - Specify coordinate system (origin top-left, x right, y down, pixels)
    - Include example API request/response formats
    - Specify error handling requirements for UI
    - Recommend HTML5 Canvas for rendering
    - Provide guidance on responsive design and user experience
    - Include testing recommendations for UI components
    - _Requirements: 1.1, 3.1, 5.1, 5.5, 6.1, 6.5, 8.1, 11.2_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Implementation uses Python for backend with Flask or FastAPI
- Frontend UI will be built by external agent based on API contract
- Checkpoints ensure incremental validation at key milestones
- Error handling is integrated throughout to ensure robust API behavior
- The backend API is designed to be stateless except for session management
- CORS must be configured to allow browser access from frontend
