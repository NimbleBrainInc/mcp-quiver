#!/usr/bin/env python3
"""
Quiver Quantitative MCP Server - FastMCP Implementation
Political and alternative financial data: congressional trades, lobbying, government contracts.
"""

import json
import os
from datetime import UTC, datetime, timedelta
from importlib.resources import files

import httpx
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

BASE_URL = "https://api.quiverquant.com"

mcp = FastMCP(
    "Quiver MCP Server",
    instructions=(
        "Before using Quiver tools, read the skill://quiver/usage resource "
        "for tool selection guidance and multi-step workflow patterns."
    ),
)

SKILL_CONTENT = files("mcp_quiver").joinpath("SKILL.md").read_text()


@mcp.resource("skill://quiver/usage")
def quiver_skill() -> str:
    """How to effectively use Quiver tools: tool selection, political data workflows."""
    return SKILL_CONTENT


def _get_api_key(api_key: str | None = None) -> str:
    """Resolve API key from parameter or environment."""
    key = api_key or os.getenv("QUIVER_API_KEY")
    if not key:
        raise ValueError("QUIVER_API_KEY environment variable is required")
    return key


def _request(path: str, api_key: str | None = None) -> list | dict:
    """Make a GET request to the Quiver API."""
    key = _get_api_key(api_key)
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {key}"},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool
def get_congress_trades(ticker: str, days_back: int = 365, api_key: str | None = None) -> str:
    """Get congressional stock trades for a ticker symbol.

    Returns trades with member name, party, chamber, transaction type,
    amount range, transaction date, and disclosure date.
    """
    try:
        data = _request(f"/beta/historical/congresstrading/{ticker.upper()}", api_key)

        if days_back and isinstance(data, list):
            cutoff = (datetime.now(UTC) - timedelta(days=days_back)).isoformat()
            data = [t for t in data if t.get("TransactionDate", "") >= cutoff[:10]]

        formatted = []
        for trade in data[:100]:
            formatted.append(
                {
                    "member": trade.get("Representative", ""),
                    "party": trade.get("Party", ""),
                    "chamber": trade.get("House", ""),
                    "transaction_type": trade.get("Transaction", ""),
                    "amount": trade.get("Amount", ""),
                    "transaction_date": trade.get("TransactionDate", ""),
                    "disclosure_date": trade.get("ReportDate", ""),
                    "ticker": trade.get("Ticker", ticker.upper()),
                }
            )

        result = {
            "ticker": ticker.upper(),
            "trades": formatted,
            "count": len(formatted),
            "days_back": days_back,
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching congress trades for {ticker}: {e}",
                "ticker": ticker.upper(),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_congress_trades_bulk(api_key: str | None = None) -> str:
    """Get all recent congressional trades across all tickers.

    Returns the latest congressional trading activity for daily ingestion
    and scanning for new activity.
    """
    try:
        data = _request("/beta/bulk/congresstrading", api_key)

        formatted = []
        for trade in (data if isinstance(data, list) else [])[:200]:
            formatted.append(
                {
                    "member": trade.get("Representative", ""),
                    "party": trade.get("Party", ""),
                    "chamber": trade.get("House", ""),
                    "transaction_type": trade.get("Transaction", ""),
                    "amount": trade.get("Amount", ""),
                    "transaction_date": trade.get("TransactionDate", ""),
                    "disclosure_date": trade.get("ReportDate", ""),
                    "ticker": trade.get("Ticker", ""),
                }
            )

        result = {
            "trades": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching bulk congress trades: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_politician_profile(name: str, api_key: str | None = None) -> str:
    """Get detailed politician profile including trading history, committees, and donors.

    This is the key tool for deep politician-level intelligence. Returns party,
    chamber, state, committees, net worth estimate, trading stats, portfolio
    holdings, campaign donors, and sponsored legislation.

    Args:
        name: Full name of the politician (e.g. "Tommy Tuberville", "Nancy Pelosi")
    """
    try:
        data = _request(f"/beta/politicians/{name}", api_key)

        result = {
            "name": name,
            "profile": data,
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching politician profile for {name}: {e}",
                "name": name,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_lobbying(ticker: str, api_key: str | None = None) -> str:
    """Get lobbying spend records for a ticker symbol.

    Returns quarterly/yearly lobbying expenditure data for the company.
    """
    try:
        data = _request(f"/beta/historical/lobbying/{ticker.upper()}", api_key)

        formatted = []
        for record in (data if isinstance(data, list) else [])[:100]:
            formatted.append(
                {
                    "client": record.get("Client", ""),
                    "amount": record.get("Amount", 0),
                    "date": record.get("Date", ""),
                    "specific_issue": record.get("SpecificIssue", ""),
                    "registrant": record.get("Registrant", ""),
                }
            )

        result = {
            "ticker": ticker.upper(),
            "lobbying_records": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching lobbying data for {ticker}: {e}",
                "ticker": ticker.upper(),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_lobbying_bulk(api_key: str | None = None) -> str:
    """Get all lobbying data across all tickers.

    Returns bulk lobbying records for scanning and ingestion.
    """
    try:
        data = _request("/beta/bulk/lobbying", api_key)

        formatted = []
        for record in (data if isinstance(data, list) else [])[:200]:
            formatted.append(
                {
                    "ticker": record.get("Ticker", ""),
                    "client": record.get("Client", ""),
                    "amount": record.get("Amount", 0),
                    "date": record.get("Date", ""),
                    "specific_issue": record.get("SpecificIssue", ""),
                    "registrant": record.get("Registrant", ""),
                }
            )

        result = {
            "lobbying_records": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching bulk lobbying data: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_gov_contracts(ticker: str, api_key: str | None = None) -> str:
    """Get government contract awards for a ticker symbol.

    Returns contract awards including quarterly amounts and individual records.
    """
    try:
        data = _request(f"/beta/historical/govcontracts/{ticker.upper()}", api_key)

        formatted = []
        for record in (data if isinstance(data, list) else [])[:100]:
            formatted.append(
                {
                    "agency": record.get("Agency", ""),
                    "amount": record.get("Amount", 0),
                    "date": record.get("Date", ""),
                    "description": record.get("Description", ""),
                }
            )

        result = {
            "ticker": ticker.upper(),
            "contracts": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching gov contracts for {ticker}: {e}",
                "ticker": ticker.upper(),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.tool
def get_gov_contracts_bulk(api_key: str | None = None) -> str:
    """Get all government contract data across all tickers.

    Returns bulk contract data for scanning and ingestion.
    """
    try:
        data = _request("/beta/bulk/govcontracts", api_key)

        formatted = []
        for record in (data if isinstance(data, list) else [])[:200]:
            formatted.append(
                {
                    "ticker": record.get("Ticker", ""),
                    "agency": record.get("Agency", ""),
                    "amount": record.get("Amount", 0),
                    "date": record.get("Date", ""),
                    "description": record.get("Description", ""),
                }
            )

        result = {
            "contracts": formatted,
            "count": len(formatted),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": f"Error fetching bulk gov contracts: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})


# ASGI entrypoint (nimbletools-core container deployment)
app = mcp.http_app()

# Stdio entrypoint (mpak / Claude Desktop)
if __name__ == "__main__":
    mcp.run()
