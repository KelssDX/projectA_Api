using System.Net.Http;
using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using Affine.Engine.Repository.Market;
using System;
using System.Linq;

namespace Affine.Engine.Services
{
    public interface IAlphaVantageService
    {
        Task<IEnumerable<MarketDataPoint>> FetchDailyTimeSeriesAsync(string symbol);
        Task<IEnumerable<MarketDataPoint>> FetchFxRateAsync(string fromSymbol, string toSymbol);
    }

    public class AlphaVantageService : IAlphaVantageService
    {
        private readonly HttpClient _httpClient;
        private readonly Microsoft.Extensions.Configuration.IConfiguration _configuration;
        private readonly string _apiKey;
        private readonly string _baseUrl;

        public AlphaVantageService(HttpClient httpClient, Microsoft.Extensions.Configuration.IConfiguration configuration) 
        {
            _httpClient = httpClient;
            _configuration = configuration;
            _apiKey = _configuration["AlphaVantage:ApiKey"] ?? "DEMO";
            _baseUrl = _configuration["AlphaVantage:BaseUrl"] ?? "https://www.alphavantage.co";
        }

        public async Task<IEnumerable<MarketDataPoint>> FetchDailyTimeSeriesAsync(string symbol)
        {
            string url = $"{_baseUrl}/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={_apiKey}";
            var response = await _httpClient.GetStringAsync(url);
            var json = JObject.Parse(response);

            var timeSeries = json["Time Series (Daily)"];
            if (timeSeries == null) return new List<MarketDataPoint>();

            var points = new List<MarketDataPoint>();
            foreach (JProperty day in timeSeries)
            {
                var date = DateTime.Parse(day.Name);
                var close = decimal.Parse(day.Value["4. close"].ToString());
                
                points.Add(new MarketDataPoint 
                { 
                    Date = date, 
                    ClosePrice = close,
                    // LogReturn calculated later during save or here if we have previous
                });
            }
            return CalculateLogReturns(points.OrderBy(p => p.Date).ToList());
        }

        public async Task<IEnumerable<MarketDataPoint>> FetchFxRateAsync(string fromSymbol, string toSymbol)
        {
             // AlphaVantage FX_DAILY
             string url = $"{_baseUrl}/query?function=FX_DAILY&from_symbol={fromSymbol}&to_symbol={toSymbol}&apikey={_apiKey}";
             var response = await _httpClient.GetStringAsync(url);
             var json = JObject.Parse(response);
             
             var timeSeries = json["Time Series FX (Daily)"];
             if (timeSeries == null) return new List<MarketDataPoint>();

             var points = new List<MarketDataPoint>();
             foreach (JProperty day in timeSeries)
             {
                 var date = DateTime.Parse(day.Name);
                 var close = decimal.Parse(day.Value["4. close"].ToString());
                 
                 points.Add(new MarketDataPoint 
                 { 
                     Date = date, 
                     ClosePrice = close 
                 });
             }
             return CalculateLogReturns(points.OrderBy(p => p.Date).ToList());
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
    }
}
