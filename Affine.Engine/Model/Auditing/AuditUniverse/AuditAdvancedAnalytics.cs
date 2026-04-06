using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class JournalExceptionAnalyticsResponse
    {
        public int? ReferenceId { get; set; }
        public int Year { get; set; }
        public int? Period { get; set; }
        public int TotalEntries { get; set; }
        public int ManualEntries { get; set; }
        public int RoundAmountEntries { get; set; }
        public int WeekendEntries { get; set; }
        public int HolidayEntries { get; set; }
        public int WeekendOrHolidayEntries { get; set; }
        public int PeriodEndEntries { get; set; }
        public int MaterialityBreaches { get; set; }
        public int UniqueUsers { get; set; }
        public decimal TotalPostedAmount { get; set; }
        public decimal MaxEntryAmount { get; set; }
        public decimal MaterialityThreshold { get; set; }
        public string MaterialityThresholdSource { get; set; }
        public string MaterialityBenchmarkSummary { get; set; }
        public decimal ManualEntryRate { get; set; }
        public decimal WeekendHolidayRate { get; set; }
        public decimal TopUserConcentrationRate { get; set; }
    }

    public class UserPostingConcentrationResponse
    {
        public int? ReferenceId { get; set; }
        public int Year { get; set; }
        public int? Period { get; set; }
        public int TotalEntries { get; set; }
        public decimal TotalPostedAmount { get; set; }
        public decimal TopUserConcentrationRate { get; set; }
        public List<UserPostingConcentrationItem> Users { get; set; } = new List<UserPostingConcentrationItem>();
    }

    public class UserPostingConcentrationItem
    {
        public string UserName { get; set; }
        public int EntryCount { get; set; }
        public decimal TotalAmount { get; set; }
        public decimal PercentageOfEntries { get; set; }
        public decimal PercentageOfValue { get; set; }
    }

    public class TrialBalanceMovementResponse
    {
        public int? ReferenceId { get; set; }
        public int CurrentYear { get; set; }
        public int PriorYear { get; set; }
        public decimal MaterialityThreshold { get; set; }
        public string MaterialityThresholdSource { get; set; }
        public string MaterialityBenchmarkSummary { get; set; }
        public int TotalAccountsCompared { get; set; }
        public int SignificantMovementsCount { get; set; }
        public decimal LargestMovementAmount { get; set; }
        public List<TrialBalanceMovementItem> Accounts { get; set; } = new List<TrialBalanceMovementItem>();
    }

    public class TrialBalanceMovementItem
    {
        public string AccountNumber { get; set; }
        public string AccountName { get; set; }
        public string Fsli { get; set; }
        public decimal PriorYearBalance { get; set; }
        public decimal CurrentYearBalance { get; set; }
        public decimal MovementAmount { get; set; }
        public decimal? MovementPercent { get; set; }
        public bool IsAboveMateriality { get; set; }
    }

    public class IndustryBenchmarkAnalyticsResponse
    {
        public int? ReferenceId { get; set; }
        public int Year { get; set; }
        public string IndustryCode { get; set; }
        public string IndustryName { get; set; }
        public int MetricsCompared { get; set; }
        public int OutsideBenchmarkCount { get; set; }
        public decimal LargestVariancePercent { get; set; }
        public List<IndustryBenchmarkMetricItem> Metrics { get; set; } = new List<IndustryBenchmarkMetricItem>();
    }

    public class IndustryBenchmarkMetricItem
    {
        public string IndustryCode { get; set; }
        public string IndustryName { get; set; }
        public string MetricName { get; set; }
        public string UnitOfMeasure { get; set; }
        public decimal CompanyValue { get; set; }
        public decimal BenchmarkMedian { get; set; }
        public decimal? BenchmarkLowerQuartile { get; set; }
        public decimal? BenchmarkUpperQuartile { get; set; }
        public decimal VariancePercent { get; set; }
        public bool IsOutsideBenchmarkRange { get; set; }
        public string BenchmarkSource { get; set; }
    }

    public class ReasonabilityForecastAnalyticsResponse
    {
        public int? ReferenceId { get; set; }
        public int Year { get; set; }
        public string ForecastBasis { get; set; }
        public decimal MaterialityThreshold { get; set; }
        public string MaterialityThresholdSource { get; set; }
        public string MaterialityBenchmarkSummary { get; set; }
        public int MetricsEvaluated { get; set; }
        public int SignificantVarianceCount { get; set; }
        public decimal LargestVarianceAmount { get; set; }
        public List<ReasonabilityForecastItem> Items { get; set; } = new List<ReasonabilityForecastItem>();
    }

    public class ReasonabilityForecastItem
    {
        public string MetricName { get; set; }
        public string MetricCategory { get; set; }
        public decimal ActualValue { get; set; }
        public decimal ExpectedValue { get; set; }
        public decimal? BudgetValue { get; set; }
        public decimal? PriorYearValue { get; set; }
        public decimal VarianceAmount { get; set; }
        public decimal? VariancePercent { get; set; }
        public bool IsAboveThreshold { get; set; }
        public string ForecastBasis { get; set; }
        public string Explanation { get; set; }
    }
}
