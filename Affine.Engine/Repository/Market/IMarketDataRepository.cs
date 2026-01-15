using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Market
{
    public interface IMarketDataRepository
    {
        Task<IEnumerable<MarketDataPoint>> GetSharePriceDataAsync(string symbol, string range = "1Y");
        Task<RiskMetrics> CalculateRiskMetricsAsync(string symbol);
        Task<IEnumerable<string>> GetAutomatedInsightsAsync(string symbol);
        Task ImportMarketDataFromCsvAsync(System.IO.Stream csvStream, string symbol);
        Task SaveMarketDataBatchAsync(IEnumerable<MarketDataPoint> data, string symbol);
        Task SeedMarketDataAsync(); // Temporary for demo
    }

    public class MarketDataPoint
    {
        public System.DateTime Date { get; set; }
        public decimal ClosePrice { get; set; }
        public double LogReturn { get; set; }
    }

    public class RiskMetrics
    {
        public string Symbol { get; set; }
        public double VaR95 { get; set; }
        public double CVaR95 { get; set; }
        public double MeanReturn { get; set; }
        public double Volatility { get; set; }
        public List<HistogramBin> Distribution { get; set; }
    }

    public class HistogramBin
    {
        public double RangeStart { get; set; }
        public double RangeEnd { get; set; }
        public int Count { get; set; }
    }
}
