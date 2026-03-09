"""
Flask application for Backend API.

Provides REST API endpoints for the Interactive Road Mapping Interface.
Integrates with RoadSegmentationModel, GraphConstructor, and PathfindingEngine.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Optional

from src.api.config import APIConfig
from src.api.exceptions import APIException, PathfindingFailedError
from src.api.logger import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)


class BackendAPI:
    """
    Flask-based REST API for Interactive Road Mapping Interface.
    
    Exposes endpoints for image loading, point selection, and pathfinding.
    Coordinates between RoadSegmentationModel, GraphConstructor, PathfindingEngine,
    and StateManager components.
    """
    
    def __init__(
        self,
        state_manager,
        segmentation_model,
        graph_constructor,
        pathfinding_engine,
        image_processor,
        point_validator,
        pathfinding_coordinator
    ):
        """
        Initialize Backend API with required components.
        
        Args:
            state_manager: StateManager instance for session management
            segmentation_model: RoadSegmentationModel instance
            graph_constructor: GraphConstructor instance
            pathfinding_engine: PathfindingEngine instance
            image_processor: ImageProcessor instance
            point_validator: PointValidator instance
            pathfinding_coordinator: PathfindingCoordinator instance
        """
        self.state_manager = state_manager
        self.segmentation_model = segmentation_model
        self.graph_constructor = graph_constructor
        self.pathfinding_engine = pathfinding_engine
        self.image_processor = image_processor
        self.point_validator = point_validator
        self.pathfinding_coordinator = pathfinding_coordinator
        
        # Create Flask app
        self.app = Flask(__name__)
        
        # Configure CORS
        CORS(self.app, origins=APIConfig.CORS_ORIGINS, supports_credentials=True)
        
        # Register error handlers
        self._register_error_handlers()
        
        # Register routes
        self._register_routes()
        
        logger.info("Backend API initialized successfully")
        logger.info(f"CORS enabled for origins: {APIConfig.CORS_ORIGINS}")
    
    def _register_error_handlers(self):
        """Register centralized error handlers for Flask app."""
        
        @self.app.errorhandler(APIException)
        def handle_api_exception(error: APIException):
            """
            Handle custom API exceptions.
            
            Maps APIException instances to appropriate HTTP responses with
            structured error format including error code, message, and details.
            """
            logger.error(
                f"API Exception: {error.error_code} - {error.message}",
                extra={
                    "error_code": error.error_code,
                    "status_code": error.status_code,
                    "details": error.details
                }
            )
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        
        @self.app.errorhandler(404)
        def handle_not_found(error):
            """Handle 404 Not Found errors."""
            logger.warning(f"Endpoint not found: {request.path}")
            return jsonify({
                "error": "Endpoint not found",
                "code": "NOT_FOUND",
                "details": f"The requested endpoint {request.path} does not exist"
            }), 404
        
        @self.app.errorhandler(500)
        def handle_internal_error(error):
            """Handle 500 Internal Server errors."""
            logger.error(f"Internal server error: {error}", exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "code": "INTERNAL_ERROR",
                "details": "An internal error occurred while processing your request"
            }), 500
        
        @self.app.errorhandler(Exception)
        def handle_unexpected_error(error):
            """
            Handle unexpected exceptions.
            
            Catches all unhandled exceptions, logs them with full stack trace,
            and returns a generic error response to avoid exposing internal details.
            """
            logger.error(
                f"Unexpected error: {type(error).__name__}: {error}",
                exc_info=True,
                extra={"error_type": type(error).__name__}
            )
            return jsonify({
                "error": "An unexpected error occurred",
                "code": "UNEXPECTED_ERROR",
                "details": "The server encountered an unexpected error"
            }), 500
        
        @self.app.before_request
        def log_request():
            """Log incoming API requests."""
            logger.info(
                f"Request: {request.method} {request.path}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                    "content_type": request.content_type
                }
            )
        
        @self.app.after_request
        def log_response(response):
            """Log API responses."""
            logger.info(
                f"Response: {request.method} {request.path} - {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "content_type": response.content_type
                }
            )
            return response
    
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.route("/api/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "version": "1.0.0"
            }), 200
        
        @self.app.route("/api/load-image", methods=["POST"])
        def load_image():
            """
            Load and process satellite image.
            
            Accepts multipart/form-data file upload, validates the image,
            performs road segmentation, constructs road graph, and returns
            image data with road mask overlay.
            
            Returns:
                JSON response with image_id, image_data, road_mask_data, width, height
            """
            import uuid
            
            try:
                # Check if file is present in request
                if 'image' not in request.files:
                    logger.warning("No image file in request")
                    return jsonify({
                        "error": "No image file provided",
                        "code": "INVALID_IMAGE",
                        "details": "Request must include 'image' file in multipart/form-data"
                    }), 400
                
                file = request.files['image']
                
                # Check if file has a filename
                if file.filename == '':
                    logger.warning("Empty filename in request")
                    return jsonify({
                        "error": "No image file selected",
                        "code": "INVALID_IMAGE",
                        "details": "File must have a valid filename"
                    }), 400
                
                # Generate unique image_id
                image_id = str(uuid.uuid4())
                logger.info(f"Processing image upload with image_id: {image_id}")
                
                # Read file data
                file_data = file.read()
                logger.debug(f"Read {len(file_data)} bytes from uploaded file")
                
                # Load and validate image using ImageProcessor
                try:
                    image = self.image_processor.load_image(file_data)
                    logger.info(f"Image loaded successfully: shape={image.shape}")
                except ValueError as e:
                    logger.error(f"Failed to load image: {e}")
                    return jsonify({
                        "error": "Invalid image file",
                        "code": "INVALID_IMAGE",
                        "details": str(e)
                    }), 400
                
                # Validate image
                if not self.image_processor.validate_image(image):
                    logger.error(f"Image validation failed: shape={image.shape}")
                    return jsonify({
                        "error": "Image validation failed",
                        "code": "INVALID_IMAGE",
                        "details": f"Image dimensions or format invalid. Max size: {self.image_processor.MAX_WIDTH}x{self.image_processor.MAX_HEIGHT}"
                    }), 400
                
                logger.info(f"Image validated successfully: {image.shape}")
                
                # Perform road segmentation
                try:
                    logger.info("Starting road segmentation")
                    # Convert image to tensor format expected by segmentation model
                    import torch
                    import numpy as np
                    
                    # Normalize image to [0, 1] range
                    image_normalized = image.astype(np.float32) / 255.0
                    
                    # Convert to tensor: (H, W, C) -> (C, H, W)
                    image_tensor = torch.from_numpy(image_normalized).permute(2, 0, 1)
                    
                    # Perform segmentation
                    road_mask = self.segmentation_model.predict(image_tensor)
                    logger.info(f"Road segmentation complete: mask shape={road_mask.shape}, road_pixels={np.sum(road_mask)}")
                    
                except Exception as e:
                    logger.error(f"Road segmentation failed: {e}", exc_info=True)
                    return jsonify({
                        "error": "Road segmentation failed",
                        "code": "SEGMENTATION_FAILED",
                        "details": str(e)
                    }), 500
                
                # Construct road graph
                try:
                    logger.info("Starting graph construction")
                    road_graph = self.graph_constructor.build_graph(road_mask)
                    logger.info(f"Graph construction complete: {road_graph.number_of_nodes()} nodes, {road_graph.number_of_edges()} edges")
                    
                except Exception as e:
                    logger.error(f"Graph construction failed: {e}", exc_info=True)
                    return jsonify({
                        "error": "Graph construction failed",
                        "code": "GRAPH_CONSTRUCTION_FAILED",
                        "details": str(e)
                    }), 500
                
                # Store state in StateManager
                self.state_manager.create_session(image_id, image, road_mask, road_graph)
                logger.info(f"Session created for image_id: {image_id}")
                
                # Encode image and mask to base64
                try:
                    image_data = self.image_processor.encode_image_to_base64(image)
                    road_mask_data = self.image_processor.encode_mask_to_base64(road_mask)
                    logger.debug("Image and mask encoded to base64")
                except Exception as e:
                    logger.error(f"Failed to encode image/mask: {e}", exc_info=True)
                    return jsonify({
                        "error": "Failed to encode image data",
                        "code": "INTERNAL_ERROR",
                        "details": str(e)
                    }), 500
                
                # Get image dimensions
                height, width = image.shape[:2]
                
                # Calculate initial statistics
                total_pixels = height * width
                road_pixels = int((road_mask > 0).sum())
                road_coverage = (road_pixels / total_pixels) * 100
                num_nodes = road_graph.number_of_nodes()
                num_edges = road_graph.number_of_edges()
                
                # Return success response with statistics
                response = {
                    "image_id": image_id,
                    "image_data": image_data,
                    "road_mask_data": road_mask_data,
                    "width": width,
                    "height": height,
                    "message": "Image processed successfully",
                    "statistics": {
                        "road_coverage_percent": round(road_coverage, 2),
                        "road_pixels": road_pixels,
                        "total_pixels": total_pixels,
                        "graph_nodes": num_nodes,
                        "graph_edges": num_edges,
                        "image_width": width,
                        "image_height": height
                    }
                }
                
                logger.info(f"Image processing complete for image_id: {image_id}")
                return jsonify(response), 200
                
            except Exception as e:
                logger.error(f"Unexpected error in load_image: {e}", exc_info=True)
                return jsonify({
                    "error": "An unexpected error occurred",
                    "code": "UNEXPECTED_ERROR",
                    "details": str(e)
                }), 500
        
        @self.app.route("/api/select-start", methods=["POST"])
        def select_start():
            """
            Select start point for pathfinding.
            
            Accepts JSON request with image_id, x, y coordinates.
            Validates that the point lies on a road pixel.
            Updates StateManager with start point if valid.
            
            Returns:
                JSON response with validation result and coordinates
            """
            try:
                # Parse JSON request
                try:
                    data = request.get_json()
                except Exception as e:
                    logger.warning(f"Failed to parse JSON: {e}")
                    return jsonify({
                        "error": "Invalid JSON data",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include valid JSON body"
                    }), 400
                
                if not data:
                    logger.warning("No JSON data in select_start request")
                    return jsonify({
                        "error": "No JSON data provided",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include JSON body with image_id, x, y"
                    }), 400
                
                # Extract parameters
                image_id = data.get('image_id')
                x = data.get('x')
                y = data.get('y')
                
                # Validate required parameters
                if image_id is None or x is None or y is None:
                    logger.warning(f"Missing required parameters: image_id={image_id}, x={x}, y={y}")
                    return jsonify({
                        "error": "Missing required parameters",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include image_id, x, and y"
                    }), 400
                
                # Validate coordinate types
                try:
                    x = int(x)
                    y = int(y)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid coordinate types: x={x}, y={y}")
                    return jsonify({
                        "error": "Invalid coordinate types",
                        "code": "INVALID_COORDINATES",
                        "details": "Coordinates x and y must be integers"
                    }), 400
                
                logger.info(f"select_start request: image_id={image_id}, x={x}, y={y}")
                
                # Validate that session exists
                if not self.state_manager.session_exists(image_id):
                    logger.warning(f"Session not found for image_id: {image_id}")
                    return jsonify({
                        "error": "Image not found",
                        "code": "IMAGE_NOT_FOUND",
                        "details": f"No session exists for image_id: {image_id}"
                    }), 404
                
                # Retrieve road_mask from StateManager
                session = self.state_manager.get_session(image_id)
                road_mask = session['road_mask']
                
                # Validate point using PointValidator
                is_valid = self.point_validator.validate_point(road_mask, x, y)
                
                if not is_valid:
                    logger.info(f"Invalid start point selected: ({x}, {y}) not on road")
                    return jsonify({
                        "valid": False,
                        "error": "Point is not on a road",
                        "coordinates": {"x": x, "y": y}
                    }), 400
                
                # Point is valid - update StateManager
                self.state_manager.set_start_point(image_id, x, y)
                logger.info(f"Start point set successfully: ({x}, {y})")
                
                # Return success response
                return jsonify({
                    "valid": True,
                    "coordinates": {"x": x, "y": y},
                    "message": "Start point selected"
                }), 200
                
            except Exception as e:
                logger.error(f"Unexpected error in select_start: {e}", exc_info=True)
                return jsonify({
                    "error": "An unexpected error occurred",
                    "code": "UNEXPECTED_ERROR",
                    "details": str(e)
                }), 500
        
        @self.app.route("/api/select-goal", methods=["POST"])
        def select_goal():
            """
            Select goal point for pathfinding.
            
            Accepts JSON request with image_id, x, y coordinates.
            Validates that the point lies on a road pixel.
            If both start and goal are set, computes shortest path.
            Updates StateManager with goal point and path if valid.
            
            Returns:
                JSON response with validation result, coordinates, and path (if computed)
            """
            try:
                # Parse JSON request
                try:
                    data = request.get_json()
                except Exception as e:
                    logger.warning(f"Failed to parse JSON: {e}")
                    return jsonify({
                        "error": "Invalid JSON data",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include valid JSON body"
                    }), 400
                
                if not data:
                    logger.warning("No JSON data in select_goal request")
                    return jsonify({
                        "error": "No JSON data provided",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include JSON body with image_id, x, y"
                    }), 400
                
                # Extract parameters
                image_id = data.get('image_id')
                x = data.get('x')
                y = data.get('y')
                
                # Validate required parameters
                if image_id is None or x is None or y is None:
                    logger.warning(f"Missing required parameters: image_id={image_id}, x={x}, y={y}")
                    return jsonify({
                        "error": "Missing required parameters",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include image_id, x, and y"
                    }), 400
                
                # Validate coordinate types
                try:
                    x = int(x)
                    y = int(y)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid coordinate types: x={x}, y={y}")
                    return jsonify({
                        "error": "Invalid coordinate types",
                        "code": "INVALID_COORDINATES",
                        "details": "Coordinates x and y must be integers"
                    }), 400
                
                logger.info(f"select_goal request: image_id={image_id}, x={x}, y={y}")
                
                # Validate that session exists
                if not self.state_manager.session_exists(image_id):
                    logger.warning(f"Session not found for image_id: {image_id}")
                    return jsonify({
                        "error": "Image not found",
                        "code": "IMAGE_NOT_FOUND",
                        "details": f"No session exists for image_id: {image_id}"
                    }), 404
                
                # Retrieve road_mask from StateManager
                session = self.state_manager.get_session(image_id)
                road_mask = session['road_mask']
                
                # Validate point using PointValidator
                is_valid = self.point_validator.validate_point(road_mask, x, y)
                
                if not is_valid:
                    logger.info(f"Invalid goal point selected: ({x}, {y}) not on road")
                    return jsonify({
                        "valid": False,
                        "error": "Point is not on a road",
                        "coordinates": {"x": x, "y": y}
                    }), 400
                
                # Point is valid - update StateManager with goal point
                self.state_manager.set_goal_point(image_id, x, y)
                logger.info(f"Goal point set successfully: ({x}, {y})")
                
                # Refresh session to get updated data
                session = self.state_manager.get_session(image_id)
                
                # Check if start_point exists
                start_point = session.get('start_point')
                
                if start_point is None:
                    # No start point yet - return success without path
                    logger.info("Goal point set, but no start point exists yet")
                    return jsonify({
                        "valid": True,
                        "coordinates": {"x": x, "y": y},
                        "path": None,
                        "message": "Goal point selected (no start point yet)"
                    }), 200
                
                # Both start and goal exist - compute path
                road_graph = session['graph']
                start_x, start_y = start_point
                
                logger.info(f"Computing path from ({start_x}, {start_y}) to ({x}, {y})")
                
                try:
                    # Invoke PathfindingCoordinator to compute path
                    path = self.pathfinding_coordinator.compute_path(
                        road_graph,
                        (start_x, start_y),
                        (x, y)
                    )
                    
                    # Store path in StateManager
                    self.state_manager.set_path(image_id, path)
                    logger.info(f"Path computed successfully: {len(path)} points")
                    
                    # Calculate path statistics
                    path_length = 0.0
                    for i in range(len(path) - 1):
                        dx = path[i+1][0] - path[i][0]
                        dy = path[i+1][1] - path[i][1]
                        path_length += (dx*dx + dy*dy) ** 0.5
                    
                    # Calculate road coverage statistics
                    total_pixels = road_mask.shape[0] * road_mask.shape[1]
                    road_pixels = int((road_mask > 0).sum())
                    road_coverage = (road_pixels / total_pixels) * 100
                    
                    # Graph statistics
                    num_nodes = road_graph.number_of_nodes()
                    num_edges = road_graph.number_of_edges()
                    
                    # Return success response with path and statistics
                    return jsonify({
                        "valid": True,
                        "coordinates": {"x": x, "y": y},
                        "path": path,
                        "message": "Goal point selected and path computed",
                        "statistics": {
                            "path_length_pixels": round(path_length, 2),
                            "path_waypoints": len(path),
                            "road_coverage_percent": round(road_coverage, 2),
                            "road_pixels": road_pixels,
                            "total_pixels": total_pixels,
                            "graph_nodes": num_nodes,
                            "graph_edges": num_edges,
                            "image_width": road_mask.shape[1],
                            "image_height": road_mask.shape[0]
                        }
                    }), 200
                    
                except PathfindingFailedError as e:
                    # Pathfinding failed - no path exists or other pathfinding error
                    logger.warning(f"Pathfinding failed: {e}")
                    return jsonify({
                        "valid": True,
                        "coordinates": {"x": x, "y": y},
                        "path": None,
                        "error": e.message,
                        "code": e.error_code,
                        "details": e.details
                    }), e.status_code
                    
                except ValueError as e:
                    # Pathfinding engine ValueError (start/goal not in graph)
                    logger.warning(f"Pathfinding ValueError: {e}")
                    return jsonify({
                        "valid": True,
                        "coordinates": {"x": x, "y": y},
                        "path": None,
                        "error": "No path exists between start and goal",
                        "code": "PATHFINDING_FAILED",
                        "details": str(e)
                    }), 400
                    
                except Exception as e:
                    # Pathfinding raised unexpected exception
                    logger.error(f"Pathfinding error: {e}", exc_info=True)
                    return jsonify({
                        "error": "Pathfinding failed",
                        "code": "PATHFINDING_FAILED",
                        "details": str(e)
                    }), 500
                
            except Exception as e:
                logger.error(f"Unexpected error in select_goal: {e}", exc_info=True)
                return jsonify({
                    "error": "An unexpected error occurred",
                    "code": "UNEXPECTED_ERROR",
                    "details": str(e)
                }), 500

        @self.app.route("/api/clear-selection", methods=["POST"])
        def clear_selection():
            """
            Clear start point, goal point, and path for a session.

            Accepts JSON request with image_id.
            Clears all selections while keeping the image and graph in memory.

            Returns:
                JSON response with success message
            """
            try:
                # Parse JSON request
                try:
                    data = request.get_json()
                except Exception as e:
                    logger.warning(f"Failed to parse JSON: {e}")
                    return jsonify({
                        "error": "Invalid JSON data",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include valid JSON body"
                    }), 400

                if not data:
                    logger.warning("No JSON data in clear_selection request")
                    return jsonify({
                        "error": "No JSON data provided",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include JSON body with image_id"
                    }), 400

                # Extract image_id parameter
                image_id = data.get('image_id')

                # Validate required parameter
                if image_id is None:
                    logger.warning("Missing image_id parameter")
                    return jsonify({
                        "error": "Missing required parameter",
                        "code": "INVALID_REQUEST",
                        "details": "Request must include image_id"
                    }), 400

                logger.info(f"clear_selection request: image_id={image_id}")

                # Validate that session exists
                if not self.state_manager.session_exists(image_id):
                    logger.warning(f"Session not found for image_id: {image_id}")
                    return jsonify({
                        "error": "Image not found",
                        "code": "IMAGE_NOT_FOUND",
                        "details": f"No session exists for image_id: {image_id}"
                    }), 404

                # Clear selection using StateManager
                self.state_manager.clear_selection(image_id)
                logger.info(f"Selection cleared successfully for image_id: {image_id}")

                # Return success response
                return jsonify({
                    "message": "Selection cleared"
                }), 200

            except Exception as e:
                logger.error(f"Unexpected error in clear_selection: {e}", exc_info=True)
                return jsonify({
                    "error": "An unexpected error occurred",
                    "code": "UNEXPECTED_ERROR",
                    "details": str(e)
                }), 500

        @self.app.route("/api/state/<image_id>", methods=["GET"])
        def get_state(image_id):
            """
            Get current state for a session.

            Accepts image_id as URL parameter.
            Returns current state including start point, goal point, and path.

            Returns:
                JSON response with session state
            """
            try:
                logger.info(f"get_state request: image_id={image_id}")

                # Validate that session exists
                if not self.state_manager.session_exists(image_id):
                    logger.warning(f"Session not found for image_id: {image_id}")
                    return jsonify({
                        "error": "Image not found",
                        "code": "IMAGE_NOT_FOUND",
                        "details": f"No session exists for image_id: {image_id}"
                    }), 404

                # Retrieve current state from StateManager
                session = self.state_manager.get_session(image_id)

                # Extract state information
                has_image = session.get('image') is not None
                start_point = session.get('start_point')
                goal_point = session.get('goal_point')
                path = session.get('path')

                # Format start_point and goal_point as dictionaries
                start_point_dict = None
                if start_point is not None:
                    start_point_dict = {"x": start_point[0], "y": start_point[1]}

                goal_point_dict = None
                if goal_point is not None:
                    goal_point_dict = {"x": goal_point[0], "y": goal_point[1]}

                # Return state response
                response = {
                    "image_id": image_id,
                    "has_image": has_image,
                    "start_point": start_point_dict,
                    "goal_point": goal_point_dict,
                    "path": path
                }

                logger.info(f"State retrieved successfully for image_id: {image_id}")
                return jsonify(response), 200

            except Exception as e:
                logger.error(f"Unexpected error in get_state: {e}", exc_info=True)
                return jsonify({
                    "error": "An unexpected error occurred",
                    "code": "UNEXPECTED_ERROR",
                    "details": str(e)
                }), 500

        
        # Additional routes will be registered by specific endpoint handlers
        # These will be implemented in subsequent tasks
        logger.info("API routes registered")
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None, debug: Optional[bool] = None):
        """
        Start the Flask development server.
        
        Args:
            host: Host address (default: from APIConfig)
            port: Port number (default: from APIConfig)
            debug: Debug mode (default: from APIConfig)
        """
        host = host or APIConfig.HOST
        port = port or APIConfig.PORT
        debug = debug if debug is not None else APIConfig.DEBUG
        
        logger.info(f"Starting Backend API server on {host}:{port} (debug={debug})")
        self.app.run(host=host, port=port, debug=debug)
    
    def get_app(self):
        """
        Get the Flask app instance.
        
        Returns:
            Flask app instance for testing or production deployment
        """
        return self.app
