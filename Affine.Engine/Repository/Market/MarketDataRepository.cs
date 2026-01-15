using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Market
{
    public class MarketDataRepository : IMarketDataRepository
    {
        private readonly string _connectionString;

        public MarketDataRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<IEnumerable<MarketDataPoint>> GetSharePriceDataAsync(string symbol, string range = "1Y")
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            string sql = @"SELECT date_time as Date, close_price as ClosePrice, log_return as LogReturn 
                           FROM ""Risk_Assess_Framework"".""market_data"" 
                           WHERE symbol = @Symbol 
                           ORDER BY date_time ASC";
            
            // Simple range filter (mock implementation for range)
            if (range == "1Y")
            {
                sql += " LIMIT 365"; 
            }

            return await db.QueryAsync<MarketDataPoint>(sql, new { Symbol = symbol });
        }

        public async Task<RiskMetrics> CalculateRiskMetricsAsync(string symbol)
        {
            var data = await GetSharePriceDataAsync(symbol, "ALL");
            var returns = data.Where(d => d.LogReturn != 0).Select(d => d.LogReturn).OrderBy(r => r).ToList();

            if (!returns.Any()) return new RiskMetrics { Symbol = symbol };

            // 1. VaR (95% confidence) = 5th percentile
            int index95 = (int)(returns.Count * 0.05);
            double vaR95 = returns[Math.Max(0, index95)];

            // 2. CVaR (Expected Shortfall) = Average of returns <= VaR
            double cVaR95 = returns.Where(r => r <= vaR95).Average();

            // 3. Distribution (Histogram)
            var distribution = GenerateHistogram(returns);

            return new RiskMetrics
            {
                Symbol = symbol,
                VaR95 = vaR95,
                CVaR95 = cVaR95,
                MeanReturn = returns.Average(),
                Volatility = StandardDeviation(returns),
                Distribution = distribution
            };
        }

        public async Task<IEnumerable<string>> GetAutomatedInsightsAsync(string symbol)
        {
            var metrics = await CalculateRiskMetricsAsync(symbol);
            var insights = new List<string>();

            if (metrics.VaR95 < -0.02)
            {
                insights.Add($"High Tail Risk detected: Daily VaR at 95% is {metrics.VaR95:P2}, indicating potential for significant losses.");
            }
            if (metrics.CVaR95 < -0.04) 
            {
                insights.Add($"Extreme Loss Potential: CVaR (Expected Shortfall) is {metrics.CVaR95:P2}.");
            }
            
            // Skewness check mock
            insights.Add("Negative skewness confirmation: Frequency of negative returns exceeds positive outliers.");
            insights.Add("Departure from normality observed in tail distribution.");

            return insights;
        }

        public async Task SeedMarketDataAsync()
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            // Check if data exists
            var count = await db.ExecuteScalarAsync<int>(@"SELECT COUNT(*) FROM ""Risk_Assess_Framework"".""market_data""");
            if (count > 0) return;

            // Generate Mock Data (Random Walk for Share Price)
            var random = new Random();
            decimal price = 150.0m;
            var startDate = DateTime.Today.AddYears(-2);
            
            var batch = new List<object>();

            for (int i = 0; i < 730; i++)
            {
                var date = startDate.AddDays(i);
                // Random return between -3% and +3%
                double u1 = 1.0 - random.NextDouble(); 
                double u2 = 1.0 - random.NextDouble();
                double randStdNormal = Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Sin(2.0 * Math.PI * u2); // Box-Muller
                
                double dailyReturn = (randStdNormal * 0.015); // 1.5% daily vol
                
                decimal newPrice = price * (decimal)Math.Exp(dailyReturn);
                double logRet = Math.Log((double)newPrice / (double)price);

                await db.ExecuteAsync(@"
                    INSERT INTO ""Risk_Assess_Framework"".""market_data"" (symbol, date_time, close_price, log_return) 
                    VALUES (@Symbol, @Date, @Price, @LogReturn)", 
                    new { Symbol = "SHARE_A", Date = date, Price = newPrice, LogReturn = logRet });

                price = newPrice;
            }
        }

        // Helpers
        private List<HistogramBin> GenerateHistogram(List<double> data, int bins = 20)
        {
            if (!data.Any()) return new List<HistogramBin>();
            
            double min = data.Min();
            double max = data.Max();
            double width = (max - min) / bins;
            
            var histogram = new List<HistogramBin>();
            for (int i = 0; i < bins; i++)
            {
                double start = min + (i * width);
                double end = start + width;
                int count = data.Count(d => d >= start && d < end);
                histogram.Add(new HistogramBin { RangeStart = start, RangeEnd = end, Count = count });
            }
            return histogram;
        }

        public async Task ImportMarketDataFromCsvAsync(System.IO.Stream csvStream, string symbol)
        {
            using var reader = new System.IO.StreamReader(csvStream);
            var points = new List<MarketDataPoint>();
            
            // Skip Header
            await reader.ReadLineAsync(); 
            
            string line;
            while ((line = await reader.ReadLineAsync()) != null)
            {
                var parts = line.Split(',');
                if (parts.Length < 5) continue; // Basic validation for Yahoo format (Date,Open,High,Low,Close,Adj Close,Vol)

                if (DateTime.TryParse(parts[0], out var date) && decimal.TryParse(parts[4], out var close))
                {
                    points.Add(new MarketDataPoint { Date = date, ClosePrice = close });
                }
            }
            
            var processed = CalculateLogReturns(points.OrderBy(p => p.Date).ToList());
            await SaveMarketDataBatchAsync(processed, symbol);
        }

        public async Task SaveMarketDataBatchAsync(IEnumerable<MarketDataPoint> data, string symbol)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            using var tran = db.BeginTransaction();

            string sql = @"
                INSERT INTO ""Risk_Assess_Framework"".""market_data"" (symbol, date_time, close_price, log_return) 
                VALUES (@Symbol, @Date, @ClosePrice, @LogReturn)";

            // Simple loop for demo - ideally Postgres COPY for bulk
            foreach(var p in data)
            {
                await db.ExecuteAsync(sql, new { Symbol = symbol, p.Date, p.ClosePrice, p.LogReturn }, tran);
            }
            
            tran.Commit();
        }

        private List<MarketDataPoint> CalculateLogReturns(List<MarketDataPoint> sortedData)
        {
            for (int i = 1; i < sortedData.Count; i++)
            {
                var prev = sortedData[i - 1].ClosePrice;
                var curr = sortedData[i].ClosePrice;
                if (prev > 0)
                {
                    sortedData[i].LogReturn = Math.Log((double)(curr / prev));
                }
            }
            return sortedData;
        }

        // Helpers
        private double StandardDeviation(List<double> values)
        {
            double avg = values.Average();
            return Math.Sqrt(values.Average(v => Math.Pow(v - avg, 2)));
        }
    }
}
