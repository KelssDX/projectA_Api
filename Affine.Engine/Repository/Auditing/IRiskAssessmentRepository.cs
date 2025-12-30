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

        // Departments CRUD
        Task<Affine.Engine.Model.Auditing.Department> CreateDepartmentAsync(Affine.Engine.Model.Auditing.Department department);
        Task<Affine.Engine.Model.Auditing.Department> UpdateDepartmentAsync(Affine.Engine.Model.Auditing.Department department);
        Task<bool> DeleteDepartmentAsync(int departmentId);

        // Projects CRUD
        Task<Affine.Engine.Model.Auditing.Project> CreateProjectAsync(Affine.Engine.Model.Auditing.Project project);
        Task<Affine.Engine.Model.Auditing.Project> UpdateProjectAsync(Affine.Engine.Model.Auditing.Project project);
        Task<bool> DeleteProjectAsync(int projectId);

        //Risk Assessment Operations
        Task<bool> AddRiskAssessmentAsync(List<RiskAssessmentCreateRequest> requests, RiskAssessmentReferenceInput reference, int? referenceId = null);
        Task<bool> UpdateRiskAssessmentsAsync(List<RiskAssessmentUpdateRequest> updates, int referenceId);
        Task<bool> DeleteRiskAssessmentAsync(int riskAssessmentId, int referenceId);
        Task<int> AddRiskAssessmentReferenceAsync(RiskAssessmentReferenceInput reference);
        Task<bool> UpdateRiskAssessmentReferenceAsync(int referenceId, RiskAssessmentReferenceInput reference);
    }
}
