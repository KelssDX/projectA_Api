-- Market Data Table for Risk Analysis
CREATE TABLE IF NOT EXISTS "Risk_Assess_Framework"."market_data" (
    "id" SERIAL PRIMARY KEY,
    "symbol" VARCHAR(50) NOT NULL,
    "date_time" TIMESTAMP NOT NULL,
    "close_price" DECIMAL(18, 6) NOT NULL,
    "log_return" DOUBLE PRECISION NOT NULL
);

-- Index for faster time-series queries
CREATE INDEX IF NOT EXISTS "idx_market_data_symbol_date" ON "Risk_Assess_Framework"."market_data"("symbol", "date_time");
