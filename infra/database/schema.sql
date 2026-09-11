CREATE TABLE IF NOT EXISTS instruments (symbol TEXT PRIMARY KEY, exchange TEXT NOT NULL, segment TEXT NOT NULL, lot_size INTEGER NOT NULL, tick_size NUMERIC NOT NULL, currency TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS candles (symbol TEXT NOT NULL, timeframe TEXT NOT NULL, timestamp TIMESTAMPTZ NOT NULL, open NUMERIC NOT NULL, high NUMERIC NOT NULL, low NUMERIC NOT NULL, close NUMERIC NOT NULL, volume NUMERIC NOT NULL, data_version TEXT NOT NULL, PRIMARY KEY(symbol,timeframe,timestamp));
CREATE TABLE IF NOT EXISTS organizations (
    organization_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('owner', 'researcher', 'trader', 'viewer')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS api_keys (
    key_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    user_id TEXT NOT NULL REFERENCES users(user_id),
    role TEXT NOT NULL CHECK (role IN ('owner', 'researcher', 'trader', 'viewer')),
    secret_digest TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS api_keys_organization_idx ON api_keys(organization_id);
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    data_version TEXT NOT NULL,
    strategy_version TEXT NOT NULL,
    code_version TEXT NOT NULL,
    parameters JSONB NOT NULL,
    universe JSONB NOT NULL,
    timeframe TEXT NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    transaction_costs JSONB NOT NULL,
    slippage JSONB NOT NULL,
    random_seed INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS experiments_organization_created_idx ON experiments(organization_id, created_at DESC);
CREATE TABLE IF NOT EXISTS experiment_results (experiment_id TEXT PRIMARY KEY REFERENCES experiments(experiment_id), metrics JSONB NOT NULL, trades JSONB NOT NULL);
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id BIGSERIAL PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'denied', 'failure')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS audit_logs_organization_created_idx ON audit_logs(organization_id, created_at DESC);
CREATE TABLE IF NOT EXISTS billing_events (
    event_id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(organization_id),
    event_type TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    provider_reference TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS billing_events_organization_occurred_idx
    ON billing_events(organization_id, occurred_at DESC);
