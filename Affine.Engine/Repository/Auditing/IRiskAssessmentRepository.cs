using Affine.Engine.Model.Auditing.Assessment;
using System;
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

        // Lookup: Departments (full details)
        Task<IEnumerable<Affine.Engine.Model.Auditing.Department>> GetDepartmentsAsync();
        // Lookup: Projects (full details)
        Task<IEnumerable<Affine.Engine.Model.Auditing.Project>> GetProjectsAsync();
        // Get all assessments
        Task<IEnumerable<object>> GetAssessmentsAsync();

        //Risk Assessment Operations
        Task<bool> AddRiskAssessmentAsync(List<RiskAssessmentCreateRequest> requests, RiskAssessmentReferenceInput reference, int? referenceId = null);
        Task<bool> UpdateRiskAssessmentsAsync(List<RiskAssessmentUpdateRequest> updates, int referenceId);
        Task<int> AddRiskAssessmentReferenceAsync(RiskAssessmentReferenceInput reference);

        // (CRUD endpoints for departments/projects can be added here when backend supports them)
    }
}
