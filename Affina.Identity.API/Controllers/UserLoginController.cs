using Affine.Engine.Repository.Identity;
using Microsoft.AspNetCore.Mvc;

namespace Affina.Identity.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class UserLoginController : ControllerBase
    {
        private readonly IUserRepository  _userRepository;

        public UserLoginController(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }

        [HttpGet]
        [Route("Login")]
        public async Task<IActionResult> Login(string email, string password)
        {
            var user = _userRepository.GetByEmailAndPassword(email, password);
            if (user == null)
            {
                return BadRequest("Invalid email or password");
            }

            // Here you can perform any additional logic based on user type if needed

            return Ok(user);
        }
    }
}