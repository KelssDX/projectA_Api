using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Model.Identity;
using Affine.Engine.Repository.Identity;
using Microsoft.AspNetCore.Mvc;

namespace Affina.Identity.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class UserLoginController : ControllerBase
    {
        private readonly IUserRepository _userRepository;
        private readonly IAuditAccessLogRepository _accessLogRepository;

        public UserLoginController(IUserRepository userRepository, IAuditAccessLogRepository accessLogRepository)
        {
            _userRepository = userRepository;
            _accessLogRepository = accessLogRepository;
        }

        [HttpGet]
        [Route("login")]
        public async Task<IActionResult> Login(string email, string password)
        {
            try
            {
                var user = await _userRepository.GetByEmailAndPasswordAsync(email, password);
                if (user == null)
                {
                    await TryLogLoginEventAsync(email, null, "Failure", "Invalid email or password");
                    return BadRequest("Invalid email or password");
                }

                if (!user.IsActive)
                {
                    await TryLogLoginEventAsync(email, user, "Failure", "User account is disabled");
                    return BadRequest("User account is disabled");
                }

                await TryLogLoginEventAsync(email, user, "Success", null);
                return Ok(user);
            }
            catch (Exception ex)
            {
                await TryLogLoginEventAsync(email, null, "Failure", ex.Message);
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("getusers")]
        public async Task<IActionResult> GetUsers()
        {
            try
            {
                var users = await _userRepository.GetAllAsync();
                return Ok(users);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("getuser/{id}")]
        public async Task<IActionResult> GetUser(int id)
        {
            try
            {
                var user = await _userRepository.GetByIdAsync(id);
                if (user == null)
                {
                    return NotFound($"User with ID {id} not found");
                }

                return Ok(user);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("getusersbyrole/{role}")]
        public async Task<IActionResult> GetUsersByRole(string role)
        {
            try
            {
                var users = await _userRepository.GetByRoleAsync(role);
                return Ok(users);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("getusersbydepartment/{departmentId}")]
        public async Task<IActionResult> GetUsersByDepartment(int departmentId)
        {
            try
            {
                var users = await _userRepository.GetByDepartmentAsync(departmentId);
                return Ok(users);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("createuser")]
        public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.Username) || string.IsNullOrEmpty(request.Email) || string.IsNullOrEmpty(request.Password))
                {
                    return BadRequest("Username, email, and password are required");
                }

                // Check if username or email already exists
                var usernameExists = await _userRepository.UsernameExistsAsync(request.Username);
                if (usernameExists)
                {
                    return BadRequest("Username already exists");
                }

                var emailExists = await _userRepository.EmailExistsAsync(request.Email);
                if (emailExists)
                {
                    return BadRequest("Email already exists");
                }

                var user = await _userRepository.CreateAsync(request);
                if (user == null)
                {
                    return BadRequest("Failed to create user");
                }

                return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("updateuser/{id}")]
        public async Task<IActionResult> UpdateUser(int id, [FromBody] UpdateUserRequest request)
        {
            try
            {
                var existingUser = await _userRepository.GetByIdAsync(id);
                if (existingUser == null)
                {
                    return NotFound($"User with ID {id} not found");
                }

                // Check if email is already taken by another user
                if (!string.IsNullOrEmpty(request.Email))
                {
                    var emailExists = await _userRepository.EmailExistsAsync(request.Email, id);
                    if (emailExists)
                    {
                        return BadRequest("Email already exists");
                    }
                }

                var updatedUser = await _userRepository.UpdateAsync(id, request);
                if (updatedUser == null)
                {
                    return BadRequest("Failed to update user");
                }

                return Ok(updatedUser);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("deleteuser/{id}")]
        public async Task<IActionResult> DeleteUser(int id)
        {
            try
            {
                var existingUser = await _userRepository.GetByIdAsync(id);
                if (existingUser == null)
                {
                    return NotFound($"User with ID {id} not found");
                }

                var success = await _userRepository.DeleteAsync(id);
                if (!success)
                {
                    return BadRequest("Failed to delete user");
                }

                return NoContent();
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("changepassword/{id}")]
        public async Task<IActionResult> ChangePassword(int id, [FromBody] ChangePasswordRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.CurrentPassword) || string.IsNullOrEmpty(request.NewPassword))
                {
                    return BadRequest("Current password and new password are required");
                }

                var existingUser = await _userRepository.GetByIdAsync(id);
                if (existingUser == null)
                {
                    return NotFound($"User with ID {id} not found");
                }

                var success = await _userRepository.ChangePasswordAsync(id, request);
                if (!success)
                {
                    return BadRequest("Current password is incorrect or failed to change password");
                }

                return Ok(new { message = "Password changed successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("toggleuserstatus/{id}")]
        public async Task<IActionResult> ToggleUserStatus(int id)
        {
            try
            {
                var existingUser = await _userRepository.GetByIdAsync(id);
                if (existingUser == null)
                {
                    return NotFound($"User with ID {id} not found");
                }

                var success = await _userRepository.SetActiveStatusAsync(id, !existingUser.IsActive);
                if (!success)
                {
                    return BadRequest("Failed to update user status");
                }

                var updatedUser = await _userRepository.GetByIdAsync(id);
                return Ok(updatedUser);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        private async Task TryLogLoginEventAsync(string? email, User? user, string status, string? failureReason)
        {
            try
            {
                await _accessLogRepository.LogLoginEventAsync(new AuditLoginEventEntry
                {
                    UserId = user?.Id,
                    Username = user?.Username ?? email,
                    DisplayName = user?.Name,
                    EventType = "Login",
                    Status = status,
                    IpAddress = HttpContext?.Connection?.RemoteIpAddress?.ToString(),
                    UserAgent = Request?.Headers?.UserAgent.ToString(),
                    ClientContext = "Identity API",
                    FailureReason = failureReason,
                    CorrelationId = HttpContext?.TraceIdentifier
                });
            }
            catch
            {
                // Authentication logging is best effort and must not block login responses.
            }
        }
    }
}
