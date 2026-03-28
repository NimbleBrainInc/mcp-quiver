# Quiver Quantitative MCP Server

[![CI](https://github.com/NimbleBrainInc/mcp-quiver/actions/workflows/ci.yml/badge.svg)](https://github.com/NimbleBrainInc/mcp-quiver/actions/workflows/ci.yml)
[![mpak](https://img.shields.io/badge/mpak-@nimblebraininc/mcp--quiver-blue)](https://mpak.dev/package/@nimblebraininc/mcp-quiver)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Political and alternative financial data MCP service powered by [Quiver Quantitative](https://www.quiverquant.com).

## Tools

| Tool | Description |
|------|-------------|
| `get_congress_trades` | Congressional stock trades for a ticker |
| `get_congress_trades_bulk` | All recent congressional trades |
| `get_politician_profile` | Deep politician profile (committees, donors, trades) |
| `get_lobbying` | Lobbying spend for a ticker |
| `get_lobbying_bulk` | All lobbying data |
| `get_gov_contracts` | Government contracts for a ticker |
| `get_gov_contracts_bulk` | All government contract data |

## Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `QUIVER_API_KEY` | Quiver Quantitative API key | Yes |

Get your API key at [quiverquant.com](https://www.quiverquant.com).

## Development

```bash
# Install dependencies
make dev-install

# Run all checks
make check

# Run server (stdio)
make run

# Run server (HTTP)
make run-http
```

## License

MIT
