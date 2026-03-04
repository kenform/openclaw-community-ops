CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS funding_rates (
  ts TIMESTAMPTZ NOT NULL,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  funding_rate DOUBLE PRECISION,
  next_funding_time TIMESTAMPTZ,
  PRIMARY KEY (ts, exchange, symbol)
);
SELECT create_hypertable('funding_rates','ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS open_interest (
  ts TIMESTAMPTZ NOT NULL,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  oi_usd DOUBLE PRECISION,
  PRIMARY KEY (ts, exchange, symbol)
);
SELECT create_hypertable('open_interest','ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS volumes (
  ts TIMESTAMPTZ NOT NULL,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  volume_24h_usd DOUBLE PRECISION,
  PRIMARY KEY (ts, exchange, symbol)
);
SELECT create_hypertable('volumes','ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS long_short (
  ts TIMESTAMPTZ NOT NULL,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  long_ratio DOUBLE PRECISION,
  short_ratio DOUBLE PRECISION,
  PRIMARY KEY (ts, exchange, symbol)
);
SELECT create_hypertable('long_short','ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS liquidations (
  ts TIMESTAMPTZ NOT NULL,
  exchange TEXT NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT,
  size_usd DOUBLE PRECISION,
  price DOUBLE PRECISION,
  PRIMARY KEY (ts, exchange, symbol, side)
);
SELECT create_hypertable('liquidations','ts', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS arb_signals (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  ex_long TEXT,
  ex_short TEXT,
  fr_spread DOUBLE PRECISION,
  est_apr DOUBLE PRECISION,
  confidence TEXT,
  PRIMARY KEY (ts, symbol, ex_long, ex_short)
);
SELECT create_hypertable('arb_signals','ts', if_not_exists => TRUE);
