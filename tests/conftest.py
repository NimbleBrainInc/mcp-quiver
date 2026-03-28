import pytest

from mcp_quiver.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp
