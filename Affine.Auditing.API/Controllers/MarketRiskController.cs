using Affine.Engine.Repository.Market;
using Affine.Engine.Services;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using System.Linq;
using System;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class MarketRiskController : ControllerBase
    {
        private readonly IMarketDataRepository _marketRepository;
        private readonly IAlphaVantageService _alphaVantageService;

        public MarketRiskController(IMarketDataRepository marketRepository, IAlphaVantageService alphaVantageService)
        {
            _marketRepository = marketRepository;
            _alphaVantageService = alphaVantageService;
        }

        [HttpGet("GetSharePriceData")]
        public async Task<IActionResult> GetSharePriceData(string symbol = "SHARE_A")
        {
            var data = await _marketRepository.GetSharePriceDataAsync(symbol);
            return Ok(data);
        }

        [HttpGet("CalculateRiskMetrics")]
        public async Task<IActionResult> CalculateRiskMetrics(string symbol = "SHARE_A")
        {
            var metrics = await _marketRepository.CalculateRiskMetricsAsync(symbol);
            return Ok(metrics);
        }

        [HttpGet("GetAutomatedInsights")]
        public async Task<IActionResult> GetAutomatedInsights(string symbol = "SHARE_A")
        {
            var insights = await _marketRepository.GetAutomatedInsightsAsync(symbol);
            return Ok(insights);
        }

        // Internal endpoint to trigger seed if needed
        [HttpPost("SeedData")]
        public async Task<IActionResult> SeedData()
        {
            await _marketRepository.SeedMarketDataAsync();
            return Ok("Market Data Seeded (Simulated)");
        }

        [HttpPost("TriggerIngestion")]
        public async Task<IActionResult> TriggerIngestion(string symbol = "IBM")
        {
            try 
            {
                var data = await _alphaVantageService.FetchDailyTimeSeriesAsync(symbol);
                if (data == null || !data.Any()) return BadRequest("No data returned from Alpha Vantage.");
                
                await _marketRepository.SaveMarketDataBatchAsync(data, symbol);
                return Ok($"Ingested {data.Count()} records for {symbol}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Ingestion failed: {ex.Message}");
            }
        }

        [HttpPost("ImportCsv")]
        public async Task<IActionResult> ImportCsv(Microsoft.AspNetCore.Http.IFormFile file, string symbol = "JSE:SOL")
        {
            if (file == null || file.Length == 0) return BadRequest("No file uploaded.");

            try
            {
                using var stream = file.OpenReadStream();
                await _marketRepository.ImportMarketDataFromCsvAsync(stream, symbol);
                return Ok($"Successfully imported market data for {symbol}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Import failed: {ex.Message}");
            }
        }
    }
}
