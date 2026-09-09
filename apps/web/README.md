# Advance Trading System Web

Next.js dashboard for the P0 research journey. It reads candles and deterministic SMC events from the FastAPI service, runs the registered backtest through the API, and lists persisted experiments.

## Run

```bash
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

The dashboard does not generate market data. If the API has no candles for the selected range, it reports that condition instead of inventing a chart or performance result.
