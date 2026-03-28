from pathlib import Path

BASE_IMAGE = "docker.io/nimbletools/mcpb-python:3.14"
CONTAINER_PORT = 8000
BUNDLE_NAME = "mcp-quiver"
BUNDLE_VERSION = "0.1.0"
PROJECT_ROOT = Path(__file__).parent.parent
