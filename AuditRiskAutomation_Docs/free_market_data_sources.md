# Free Market Data Sources (API + CSV)

This document lists **100% FREE** market data sources that can be used to populate the `market_data` table with **real historical prices** (no paid plans, no trials required).

It covers:
- Equities (including JSE)
- Indices
- FX rates
- API and CSV download options

---

## 1. Yahoo Finance (FREE CSV – Best for JSE)

**Type**: Manual CSV download  
**Cost**: Free  
**Signup**: None  

**Website**  
https://finance.yahoo.com

### What you get
- JSE equities (`.JO`)
- JSE indices
- Global equities
- Historical daily prices
- Adjusted close prices

### How to download CSV
1. Open a symbol page
2. Click **Historical Data**
3. Click **Download**

### JSE Examples
- Sasol: https://finance.yahoo.com/quote/SOL.JO  
- Naspers: https://finance.yahoo.com/quote/NPN.JO  
- FirstRand: https://finance.yahoo.com/quote/FSR.JO  
- JSE All Share Index: https://finance.yahoo.com/quote/%5EJ203.JO

**Best for**
- CSV upload feature
- Initial and ongoing data loads
- Risk metrics (VaR / CVaR / Volatility)

---

## 2. Alpha Vantage (FREE API + CSV)

**Type**: REST API  
**Cost**: Free tier  
**Limits**: 25 requests per day  
**Signup**: Required (free API key)

**Website**  
https://www.alphavantage.co

### What you get
- Daily equity prices
- FX rates
- CSV or JSON output
- Historical time series

### Equity API Example (CSV)
```
https://www.alphavantage.co/query?
function=TIME_SERIES_DAILY_ADJUSTED
&symbol=IBM
&apikey=YOUR_API_KEY
&datatype=csv
```

### FX API Example (CSV)
```
https://www.alphavantage.co/query?
function=FX_DAILY
&from_symbol=USD
&to_symbol=ZAR
&apikey=YOUR_API_KEY
&datatype=csv
```

**Notes**
- FX coverage is excellent
- JSE equity coverage is limited

**Best for**
- Automated ingestion
- FX risk data (USD/ZAR, GBP/ZAR, EUR/ZAR)

---

## 3. South African Reserve Bank (SARB) – FREE FX CSV

**Type**: CSV / Excel downloads  
**Cost**: Free  
**Signup**: None  

**Website**  
https://www.resbank.co.za/en/home/what-we-do/statistics

### What you get
- Official ZAR exchange rates
- USD/ZAR, GBP/ZAR, EUR/ZAR
- Historical data
- Central-bank authoritative source

**Best for**
- FX exposure
- Audit-grade exchange rates
- South African risk reporting

---

## 4. Stooq (FREE CSV – Global Markets)

**Type**: Direct CSV download  
**Cost**: Free  
**Signup**: None  

**Website**  
https://stooq.com/db

### Example CSV Link
```
https://stooq.com/q/d/l/?s=aapl.us&i=d
```

### What you get
- Global equities
- Indices
- Long historical ranges

**Notes**
- JSE coverage is weak
- Useful for testing ingestion pipelines

---

## 5. Recommended FREE Setup for Affine

### Equities (JSE)
- Yahoo Finance CSV  
  https://finance.yahoo.com

### FX Rates
- SARB CSV (Primary)  
  https://www.resbank.co.za/en/home/what-we-do/statistics
- Alpha Vantage API (Secondary / Automation)  
  https://www.alphavantage.co

---

## 6. Data Format Required (Matches Existing Schema)

Your `market_data` table already supports everything needed:

| Column        | Description                   |
|---------------|-------------------------------|
| symbol        | Ticker or FX code             |
| date_time     | Trading date                  |
| close_price   | Close / adjusted close price  |
| log_return    | Calculated on import          |

### Log Return Formula
```
log_return = ln(price_today / price_yesterday)
```

No schema changes required.

---

## 7. Practical Next Step

Replace `SeedMarketDataAsync()` with:
- CSV upload (Yahoo / SARB), or
- API ingestion (Alpha Vantage)

This immediately switches dashboards from **simulated data** to **real market history**.

---

**Cost**: Free  
**API Available**: Yes  
**CSV Available**: Yes  
**Production Ready**: Yes (with rate limits)

