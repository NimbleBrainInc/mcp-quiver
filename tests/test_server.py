"""Tests for Quiver MCP Server."""

import json
import os
from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_quiver.server import mcp


@pytest.fixture
def client():
    return Client(mcp)


class TestSkillResource:
    """Test the embedded skill resource."""

    @pytest.mark.asyncio
    async def test_initialize_returns_instructions(self, client):
        async with client:
            init = await client.initialize()
            assert "skill://quiver/usage" in init.instructions

    @pytest.mark.asyncio
    async def test_skill_resource_listed(self, client):
        async with client:
            resources = await client.list_resources()
            uris = [str(r.uri) for r in resources]
            assert "skill://quiver/usage" in uris

    @pytest.mark.asyncio
    async def test_skill_resource_readable(self, client):
        async with client:
            content = await client.read_resource("skill://quiver/usage")
            text = content[0].text if hasattr(content[0], "text") else str(content[0])
            assert "get_congress_trades" in text
            assert "get_politician_profile" in text


class TestToolListing:
    """Test that all tools are registered."""

    @pytest.mark.asyncio
    async def test_tools_list(self, client):
        async with client:
            tools = await client.list_tools()
            names = {t.name for t in tools}
            expected = {
                "get_congress_trades",
                "get_congress_trades_bulk",
                "get_politician_profile",
                "get_lobbying",
                "get_lobbying_bulk",
                "get_gov_contracts",
                "get_gov_contracts_bulk",
            }
            assert expected == names

    @pytest.mark.asyncio
    async def test_tool_count(self, client):
        async with client:
            tools = await client.list_tools()
            assert len(tools) == 7

    @pytest.mark.asyncio
    async def test_tool_descriptions_present(self, client):
        async with client:
            tools = await client.list_tools()
            for tool in tools:
                assert tool.description, f"Tool {tool.name} missing description"


class TestRequiredParameters:
    """Test required parameter validation."""

    @pytest.mark.asyncio
    async def test_congress_trades_missing_ticker(self, client):
        async with client:
            try:
                await client.call_tool("get_congress_trades", {})
                raise AssertionError("Should have raised an exception")
            except Exception as e:
                assert "ticker" in str(e).lower() or "required" in str(e).lower()

    @pytest.mark.asyncio
    async def test_politician_profile_missing_name(self, client):
        async with client:
            try:
                await client.call_tool("get_politician_profile", {})
                raise AssertionError("Should have raised an exception")
            except Exception as e:
                assert "name" in str(e).lower() or "required" in str(e).lower()

    @pytest.mark.asyncio
    async def test_lobbying_missing_ticker(self, client):
        async with client:
            try:
                await client.call_tool("get_lobbying", {})
                raise AssertionError("Should have raised an exception")
            except Exception as e:
                assert "ticker" in str(e).lower() or "required" in str(e).lower()

    @pytest.mark.asyncio
    async def test_gov_contracts_missing_ticker(self, client):
        async with client:
            try:
                await client.call_tool("get_gov_contracts", {})
                raise AssertionError("Should have raised an exception")
            except Exception as e:
                assert "ticker" in str(e).lower() or "required" in str(e).lower()

    @pytest.mark.asyncio
    async def test_invalid_tool(self, client):
        async with client:
            try:
                await client.call_tool("invalid_tool", {})
                raise AssertionError("Should have raised an exception")
            except Exception as e:
                assert "invalid_tool" in str(e).lower() or "not found" in str(e).lower()


class TestErrorHandling:
    """Test graceful error handling without API key."""

    @pytest.mark.asyncio
    async def test_congress_trades_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_congress_trades", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data
                assert "QUIVER_API_KEY" in data["error"]

    @pytest.mark.asyncio
    async def test_politician_profile_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_politician_profile", {"name": "Nancy Pelosi"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data

    @pytest.mark.asyncio
    async def test_lobbying_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_lobbying", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data

    @pytest.mark.asyncio
    async def test_gov_contracts_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_gov_contracts", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data

    @pytest.mark.asyncio
    async def test_bulk_trades_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_congress_trades_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data

    @pytest.mark.asyncio
    async def test_lobbying_bulk_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_lobbying_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data

    @pytest.mark.asyncio
    async def test_gov_contracts_bulk_no_api_key(self, client):
        with patch.dict(os.environ, {}, clear=True):
            async with client:
                result = await client.call_tool("get_gov_contracts_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert "error" in data


class TestWithMockedAPI:
    """Test tool logic with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_get_congress_trades_with_mock(self, client):
        mock_data = [
            {
                "Representative": "Tommy Tuberville",
                "Party": "Republican",
                "House": "Senate",
                "Transaction": "Purchase",
                "Amount": "$1,001 - $15,000",
                "TransactionDate": "2026-03-15",
                "ReportDate": "2026-03-20",
                "Ticker": "AAPL",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_congress_trades", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["trades"][0]["member"] == "Tommy Tuberville"
                assert data["trades"][0]["party"] == "Republican"
                assert data["trades"][0]["transaction_type"] == "Purchase"
                assert data["ticker"] == "AAPL"
                assert "retrieved_at" in data

    @pytest.mark.asyncio
    async def test_get_congress_trades_days_back_filter(self, client):
        """Test that days_back filters old trades."""
        mock_data = [
            {
                "Representative": "Old Trade",
                "TransactionDate": "2020-01-01",
                "Ticker": "AAPL",
            },
            {
                "Representative": "Recent Trade",
                "TransactionDate": "2026-03-15",
                "Ticker": "AAPL",
            },
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool(
                    "get_congress_trades", {"ticker": "AAPL", "days_back": 90}
                )
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["trades"][0]["member"] == "Recent Trade"

    @pytest.mark.asyncio
    async def test_get_congress_trades_ticker_uppercased(self, client):
        """Test that ticker is uppercased in the response."""
        with patch("mcp_quiver.server._request", return_value=[]):
            async with client:
                result = await client.call_tool("get_congress_trades", {"ticker": "aapl"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_congress_trades_caps_at_100(self, client):
        """Test that results are capped at 100."""
        mock_data = [
            {
                "Representative": f"Member {i}",
                "TransactionDate": "2026-03-15",
                "Ticker": "AAPL",
            }
            for i in range(150)
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_congress_trades", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 100

    @pytest.mark.asyncio
    async def test_get_lobbying_with_mock(self, client):
        mock_data = [
            {
                "Client": "Apple Inc",
                "Amount": 2500000,
                "Date": "2025-Q1",
                "SpecificIssue": "Privacy legislation",
                "Registrant": "Lobbying Firm LLC",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_lobbying", {"ticker": "AAPL"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["lobbying_records"][0]["client"] == "Apple Inc"
                assert data["lobbying_records"][0]["amount"] == 2500000
                assert data["lobbying_records"][0]["specific_issue"] == "Privacy legislation"
                assert data["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_gov_contracts_with_mock(self, client):
        mock_data = [
            {
                "Agency": "Department of Defense",
                "Amount": 50000000,
                "Date": "2025-01-01",
                "Description": "Cloud infrastructure services",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_gov_contracts", {"ticker": "MSFT"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["contracts"][0]["agency"] == "Department of Defense"
                assert data["contracts"][0]["amount"] == 50000000
                assert data["ticker"] == "MSFT"

    @pytest.mark.asyncio
    async def test_get_politician_profile_with_mock(self, client):
        mock_data = {
            "name": "Nancy Pelosi",
            "party": "Democrat",
            "chamber": "House",
            "state": "CA",
            "committees": ["Financial Services"],
        }

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_politician_profile", {"name": "Nancy Pelosi"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["name"] == "Nancy Pelosi"
                assert data["profile"]["party"] == "Democrat"
                assert data["profile"]["state"] == "CA"
                assert "retrieved_at" in data

    @pytest.mark.asyncio
    async def test_bulk_trades_with_mock(self, client):
        mock_data = [
            {
                "Representative": "Member A",
                "Party": "Democrat",
                "House": "House",
                "Transaction": "Sale (Full)",
                "Amount": "$15,001 - $50,000",
                "TransactionDate": "2025-03-01",
                "ReportDate": "2025-03-15",
                "Ticker": "TSLA",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_congress_trades_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["trades"][0]["ticker"] == "TSLA"
                assert data["trades"][0]["transaction_type"] == "Sale (Full)"

    @pytest.mark.asyncio
    async def test_bulk_trades_caps_at_200(self, client):
        """Test that bulk results are capped at 200."""
        mock_data = [{"Representative": f"Member {i}", "Ticker": f"T{i}"} for i in range(300)]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_congress_trades_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 200

    @pytest.mark.asyncio
    async def test_lobbying_bulk_with_mock(self, client):
        mock_data = [
            {
                "Ticker": "AAPL",
                "Client": "Apple Inc",
                "Amount": 1000000,
                "Date": "2025-Q1",
                "SpecificIssue": "Tax policy",
                "Registrant": "Firm A",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_lobbying_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["lobbying_records"][0]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_gov_contracts_bulk_with_mock(self, client):
        mock_data = [
            {
                "Ticker": "LMT",
                "Agency": "DoD",
                "Amount": 100000000,
                "Date": "2025-01-15",
                "Description": "F-35 maintenance",
            }
        ]

        with patch("mcp_quiver.server._request", return_value=mock_data):
            async with client:
                result = await client.call_tool("get_gov_contracts_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 1
                assert data["contracts"][0]["ticker"] == "LMT"
                assert data["contracts"][0]["agency"] == "DoD"

    @pytest.mark.asyncio
    async def test_empty_response_handling(self, client):
        """Test that empty API responses are handled gracefully."""
        with patch("mcp_quiver.server._request", return_value=[]):
            async with client:
                result = await client.call_tool("get_lobbying", {"ticker": "ZZZZ"})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 0
                assert data["lobbying_records"] == []

    @pytest.mark.asyncio
    async def test_non_list_response_handling(self, client):
        """Test that non-list API responses don't crash bulk tools."""
        with patch("mcp_quiver.server._request", return_value={"error": "bad request"}):
            async with client:
                result = await client.call_tool("get_lobbying_bulk", {})
                text = result.content[0].text if hasattr(result, "content") else result[0].text
                data = json.loads(text)
                assert data["count"] == 0
