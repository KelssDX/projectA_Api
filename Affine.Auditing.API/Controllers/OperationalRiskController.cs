using Affine.Engine.Repository.Operational;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class OperationalRiskController : ControllerBase
    {
        private readonly IOperationalRiskRepository _repository;

        public OperationalRiskController(IOperationalRiskRepository repository)
        {
            _repository = repository;
        }

        [HttpGet("GetOperationalRisks")]
        public async Task<IActionResult> GetOperationalRisks(int referenceId)
        {
            var data = await _repository.GetOperationalRisksAsync(referenceId);
            return Ok(data);
        }
    }
}
