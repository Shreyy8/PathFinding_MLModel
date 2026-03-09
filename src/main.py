"""
Main application entry point for Interactive Road Mapping Interface.

This module initializes all backend components and starts the Flask API server.
It wires together:
- RoadSegmentationModel for road detection
- GraphConstructor for graph building
- PathfindingEngine for route computation
- StateManager for session management
- ImageProcessor for image handling
- PointValidator for coordinate validation
- PathfindingCoordinator for pathfinding coordination
- BackendAPI for REST API endpoints

Requirements: 10.1, 10.2, 10.3
"""

import logging
import argparse
import sys
import os
import warnings

# Suppress NumPy warnings related to Python 3.13 compatibility
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')
warnings.filterwarnings('ignore', message='invalid value encountered')

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.road_segmentation_model import RoadSegmentationModel
from src.graph_constructor import GraphConstructor
from src.pathfinding_engine import PathfindingEngine
from src.api.state_manager import StateManager
from src.api.point_validator import PointValidator
from src.api.image_processor import ImageProcessor
from src.api.pathfinding_coordinator import PathfindingCoordinator
from src.api.app import BackendAPI
from src.api.config import APIConfig
from src.api.logger import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)


def initialize_components():
    """
    Initialize all backend components.
    
    Creates and configures:
    - RoadSegmentationModel with pretrained weights
    - GraphConstructor with 8-connectivity
    - PathfindingEngine with A* algorithm
    - StateManager for session management
    - PointValidator for coordinate validation
    - ImageProcessor for image handling
    - PathfindingCoordinator for pathfinding coordination
    
    Returns:
        Dictionary containing all initialized components
    
    Raises:
        RuntimeError: If component initialization fails
    """
    logger.info("Initializing backend components...")
    
    try:
        # Initialize RoadSegmentationModel
        logger.info("Initializing RoadSegmentationModel...")
        segmentation_model = RoadSegmentationModel()
        
        # Load checkpoint if available
        checkpoint_path = APIConfig.MODEL_CHECKPOINT_PATH
        if os.path.exists(checkpoint_path):
            logger.info(f"Loading model checkpoint from {checkpoint_path}")
            segmentation_model.load_checkpoint(checkpoint_path)
        else:
            logger.warning(f"Model checkpoint not found at {checkpoint_path}, using untrained model")
        
        # Initialize GraphConstructor with 8-connectivity
        logger.info("Initializing GraphConstructor...")
        graph_constructor = GraphConstructor(connectivity=8)
        
        # Initialize PathfindingEngine with A* algorithm
        logger.info("Initializing PathfindingEngine...")
        pathfinding_engine = PathfindingEngine(algorithm="astar")
        
        # Initialize StateManager
        logger.info("Initializing StateManager...")
        state_manager = StateManager()
        
        # Initialize PointValidator
        logger.info("Initializing PointValidator...")
        point_validator = PointValidator()
        
        # Initialize ImageProcessor
        logger.info("Initializing ImageProcessor...")
        image_processor = ImageProcessor()
        
        # Initialize PathfindingCoordinator
        logger.info("Initializing PathfindingCoordinator...")
        pathfinding_coordinator = PathfindingCoordinator(pathfinding_engine)
        
        logger.info("All components initialized successfully")
        
        return {
            'segmentation_model': segmentation_model,
            'graph_constructor': graph_constructor,
            'pathfinding_engine': pathfinding_engine,
            'state_manager': state_manager,
            'point_validator': point_validator,
            'image_processor': image_processor,
            'pathfinding_coordinator': pathfinding_coordinator
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        raise RuntimeError(f"Component initialization failed: {e}")


def create_app():
    """
    Create and configure the Flask application.
    
    Initializes all backend components and creates the BackendAPI instance
    with proper dependency injection.
    
    Returns:
        Flask application instance
    
    Raises:
        RuntimeError: If application creation fails
    """
    logger.info("Creating Flask application...")
    
    try:
        # Initialize all components
        components = initialize_components()
        
        # Create BackendAPI with all components
        logger.info("Creating BackendAPI...")
        backend_api = BackendAPI(
            state_manager=components['state_manager'],
            segmentation_model=components['segmentation_model'],
            graph_constructor=components['graph_constructor'],
            pathfinding_engine=components['pathfinding_engine'],
            image_processor=components['image_processor'],
            point_validator=components['point_validator'],
            pathfinding_coordinator=components['pathfinding_coordinator']
        )
        
        logger.info("Flask application created successfully")
        
        return backend_api
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}", exc_info=True)
        raise RuntimeError(f"Application creation failed: {e}")


def main():
    """
    Main entry point for the application.
    
    Parses command-line arguments, creates the Flask application,
    and starts the development server.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Interactive Road Mapping Interface - Backend API Server'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help=f'Host address to bind to (default: {APIConfig.HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help=f'Port number to bind to (default: {APIConfig.PORT})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=None,
        help=f'Enable debug mode (default: {APIConfig.DEBUG})'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug mode'
    )
    
    args = parser.parse_args()
    
    # Determine debug mode
    debug = None
    if args.debug:
        debug = True
    elif args.no_debug:
        debug = False
    
    # Log startup information
    logger.info("=" * 80)
    logger.info("Interactive Road Mapping Interface - Backend API Server")
    logger.info("=" * 80)
    logger.info(f"Host: {args.host or APIConfig.HOST}")
    logger.info(f"Port: {args.port or APIConfig.PORT}")
    logger.info(f"Debug: {debug if debug is not None else APIConfig.DEBUG}")
    logger.info("=" * 80)
    
    try:
        # Create Flask application
        backend_api = create_app()
        
        # Start the server
        logger.info("Starting Flask development server...")
        backend_api.run(
            host=args.host,
            port=args.port,
            debug=debug
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed to start: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
