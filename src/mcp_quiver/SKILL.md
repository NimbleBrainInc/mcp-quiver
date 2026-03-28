# Quiver Quantitative — Tool Usage Guide

**Critical:** Reuse data from prior tool calls in the conversation. Do not re-fetch data you already have.

## Tool Selection

| Intent | Tool |
|--------|------|
| Congressional trades for a specific stock | `get_congress_trades` |
| Scan all recent congressional trading activity | `get_congress_trades_bulk` |
| Deep dive on a specific politician | `get_politician_profile` |
| Lobbying spend for a company | `get_lobbying` |
| Scan all lobbying activity | `get_lobbying_bulk` |
| Government contracts for a company | `get_gov_contracts` |
| Scan all government contract awards | `get_gov_contracts_bulk` |

## Parameters

- **ticker**: Always uppercase US ticker symbols (e.g., AAPL, MSFT, LMT, BA)
- **name**: Full politician name as it appears in congressional records (e.g., "Tommy Tuberville", "Nancy Pelosi")
- **days_back**: Filters trades client-side — use smaller values (90, 180) to focus on recent activity

## Multi-Step Workflows

### Political-Financial Intelligence on a Stock
1. `get_congress_trades` — who in Congress is trading this stock?
2. `get_lobbying` — how much is the company spending on lobbying?
3. `get_gov_contracts` — does the company have government contracts?
4. For each active politician found in step 1: `get_politician_profile` — deep dive

### Politician Investigation
1. `get_politician_profile` — full profile with committees, donors, trading stats
2. For tickers in their portfolio: `get_congress_trades` — detailed trade history per stock

### Daily Scan / Ingestion
1. `get_congress_trades_bulk` — all recent congressional trades
2. `get_lobbying_bulk` — all recent lobbying records
3. `get_gov_contracts_bulk` — all recent contract awards
4. Cross-reference: identify tickers that appear in multiple datasets

### Influence Graph Construction
1. `get_lobbying` + `get_gov_contracts` for a ticker — corporate influence footprint
2. `get_congress_trades` for same ticker — which politicians are trading it
3. `get_politician_profile` for active traders — committee assignments and donors

## Key Data Points

- **Congress trades**: Transaction types are "Purchase" or "Sale (Full/Partial)". Amount is a range (e.g., "$1,001 - $15,000")
- **Lobbying**: Amount is in dollars. Records include the specific issue lobbied on
- **Gov contracts**: Amount is the contract value. Agency identifies the government body
- **Politician profiles**: Include committee assignments (key for identifying conflicts of interest), campaign donors, and aggregate trading statistics
