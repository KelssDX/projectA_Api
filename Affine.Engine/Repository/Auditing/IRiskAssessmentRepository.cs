using Affine.Engine.Model.Auditing.Assessment;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IRiskAssessmentRepository
    {
        //Original Method
        Task<RiskAssessment_Assessment> GetRiskAssessmentAsync(int RiskAssessmentRefID);

        //Methods for Dropdowns
        Task<Risks_Assessment> GetRisksAsync(string email, string password);
        Task<Controls_Assessment> GetControlsAsync(string email, string password);
        Task<Outcome_Assessment> GetOutcomesAsync(string email, string password);

        //Methods for RA_Tables
        Task<IEnumerable<RiskLikelihood>> GetRiskLikelihoodsAsync();
        Task<IEnumerable<Impact>> GetImpactsAsync();
        Task<IEnumerable<KeySecondary>> GetKeySecondaryRisksAsync();
        Task<IEnumerable<RiskCategory>> GetRiskCategoriesAsync();
        Task<IEnumerable<DataFrequency>> GetDataFrequenciesAsync();
        Task<IEnumerable<OutcomeLikelihood>> GetOutcomeLikelihoodsAsync();
        Task<IEnumerable<Evidence>> GetEvidenceAsync();

        //Risk Assessment Operations
        Task<bool> AddRiskAssessmentAsync(List<RiskAssessmentCreateRequest> requests);
       //  Task<bool>  UpdateRiskAssessmentsAsync(List<RiskAssessmentUpdateRequest> updates, int referenceId);
        Task<bool> UpdateRiskAssessmentAsync(int riskAssessmentRefId, RiskAssessmentUpdateRequest request);

    }
}
