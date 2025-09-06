using Affine.Engine.Model.Identity;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Identity
{
    public interface IUserRepository
    {
        // Authentication methods
        User GetByEmailAndPassword(string email, string password);
        Task<User> GetByEmailAndPasswordAsync(string email, string password);
        
        // User CRUD operations
        Task<User> GetByIdAsync(int id);
        Task<User> GetByUsernameAsync(string username);
        Task<User> GetByEmailAsync(string email);
        Task<IEnumerable<User>> GetAllAsync();
        Task<IEnumerable<User>> GetByRoleAsync(string role);
        Task<IEnumerable<User>> GetByDepartmentAsync(int departmentId);
        Task<User> CreateAsync(CreateUserRequest request);
        Task<User> UpdateAsync(int id, UpdateUserRequest request);
        Task<bool> DeleteAsync(int id);
        
        // Password management
        Task<bool> ChangePasswordAsync(int id, ChangePasswordRequest request);
        Task<bool> ValidatePasswordAsync(int id, string password);
        
        // User status management
        Task<bool> SetActiveStatusAsync(int id, bool isActive);
        
        // Validation methods
        Task<bool> UsernameExistsAsync(string username);
        Task<bool> EmailExistsAsync(string email);
        Task<bool> EmailExistsAsync(string email, int excludeUserId);
    }
}
