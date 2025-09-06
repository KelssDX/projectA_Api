using Affine.Engine.Model.Identity;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Identity
{
    public class UserRepository : IUserRepository
    {
        private readonly string _connectionString;

        public UserRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        // Authentication methods
        public User GetByEmailAndPassword(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE email = @Email AND EXISTS (
                    SELECT 1 FROM accounts WHERE email = @Email AND password = @Password
                );";

            return dbConnection.QueryFirstOrDefault<User>(query, new { Email = email, Password = password });
        }

        public async Task<User> GetByEmailAndPasswordAsync(string email, string password)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE email = @Email AND EXISTS (
                    SELECT 1 FROM accounts WHERE email = @Email AND password = @Password
                );";

            return await dbConnection.QueryFirstOrDefaultAsync<User>(query, new { Email = email, Password = password });
        }

        // User CRUD operations
        public async Task<User> GetByIdAsync(int id)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE id = @Id;";

            return await dbConnection.QueryFirstOrDefaultAsync<User>(query, new { Id = id });
        }

        public async Task<User> GetByUsernameAsync(string username)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE username = @Username;";

            return await dbConnection.QueryFirstOrDefaultAsync<User>(query, new { Username = username });
        }

        public async Task<User> GetByEmailAsync(string email)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE email = @Email;";

            return await dbConnection.QueryFirstOrDefaultAsync<User>(query, new { Email = email });
        }

        public async Task<IEnumerable<User>> GetAllAsync()
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                ORDER BY name;";

            return await dbConnection.QueryAsync<User>(query);
        }

        public async Task<IEnumerable<User>> GetByRoleAsync(string role)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    id, username, name, email, role, department, is_active AS IsActive, created_at, updated_at
                FROM user_view 
                WHERE role = @Role
                ORDER BY name;";

            return await dbConnection.QueryAsync<User>(query, new { Role = role });
        }

        public async Task<IEnumerable<User>> GetByDepartmentAsync(int departmentId)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = @"
                SELECT 
                    u.id, u.username, u.name, u.email, u.role, u.department, u.is_active AS IsActive, u.created_at, u.updated_at
                FROM user_view u
                JOIN accounts a ON u.id = a.user_id
                WHERE a.department_id = @DepartmentId
                ORDER BY u.name;";

            return await dbConnection.QueryAsync<User>(query, new { DepartmentId = departmentId });
        }

        public async Task<User> CreateAsync(CreateUserRequest request)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            // Check if username or email already exists
            var existingUser = await dbConnection.QueryFirstOrDefaultAsync<int?>(
                "SELECT user_id FROM accounts WHERE username = @Username OR email = @Email",
                new { Username = request.Username, Email = request.Email });

            if (existingUser.HasValue)
                return null; // Username or email already exists

            string insertQuery = @"
                INSERT INTO accounts (username, password, firstname, lastname, email, role_id, department_id)
                VALUES (@Username, @Password, @Firstname, @Lastname, @Email, @RoleId, @DepartmentId)
                RETURNING user_id;";

            var userId = await dbConnection.QueryFirstOrDefaultAsync<int>(insertQuery, new
            {
                Username = request.Username,
                Password = request.Password, // Should be hashed in production
                Firstname = request.Firstname,
                Lastname = request.Lastname,
                Email = request.Email,
                RoleId = request.RoleId ?? 3, // Default to 'user' role
                DepartmentId = request.DepartmentId
            });

            return await GetByIdAsync(userId);
        }

        public async Task<User> UpdateAsync(int id, UpdateUserRequest request)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            // Check if email is already taken by another user
            if (!string.IsNullOrEmpty(request.Email))
            {
                var existingUser = await dbConnection.QueryFirstOrDefaultAsync<int?>(
                    "SELECT user_id FROM accounts WHERE email = @Email AND user_id != @Id",
                    new { Email = request.Email, Id = id });

                if (existingUser.HasValue)
                    return null; // Email already taken
            }

            string updateQuery = @"
                UPDATE accounts SET 
                    firstname = COALESCE(@Firstname, firstname),
                    lastname = COALESCE(@Lastname, lastname),
                    email = COALESCE(@Email, email),
                    role_id = COALESCE(@RoleId, role_id),
                    department_id = COALESCE(@DepartmentId, department_id),
                    is_active = COALESCE(@IsActive, is_active),
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = @Id;";

            await dbConnection.ExecuteAsync(updateQuery, new
            {
                Id = id,
                Firstname = request.Firstname,
                Lastname = request.Lastname,
                Email = request.Email,
                RoleId = request.RoleId,
                DepartmentId = request.DepartmentId,
                IsActive = request.IsActive
            });

            return await GetByIdAsync(id);
        }

        public async Task<bool> DeleteAsync(int id)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string deleteQuery = "DELETE FROM accounts WHERE user_id = @Id;";
            var rowsAffected = await dbConnection.ExecuteAsync(deleteQuery, new { Id = id });

            return rowsAffected > 0;
        }

        // Password management
        public async Task<bool> ChangePasswordAsync(int id, ChangePasswordRequest request)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            // Verify current password
            var isValidPassword = await ValidatePasswordAsync(id, request.CurrentPassword);
            if (!isValidPassword)
                return false;

            // Update password
            string updateQuery = @"
                UPDATE accounts SET 
                    password = @NewPassword,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = @Id;";

            var rowsAffected = await dbConnection.ExecuteAsync(updateQuery, new
            {
                Id = id,
                NewPassword = request.NewPassword // Should be hashed in production
            });

            return rowsAffected > 0;
        }

        public async Task<bool> ValidatePasswordAsync(int id, string password)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = "SELECT COUNT(1) FROM accounts WHERE user_id = @Id AND password = @Password;";
            var count = await dbConnection.QueryFirstOrDefaultAsync<int>(query, new { Id = id, Password = password });

            return count > 0;
        }

        // User status management
        public async Task<bool> SetActiveStatusAsync(int id, bool isActive)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string updateQuery = @"
                UPDATE accounts SET 
                    is_active = @IsActive,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = @Id;";

            var rowsAffected = await dbConnection.ExecuteAsync(updateQuery, new { Id = id, IsActive = isActive });

            return rowsAffected > 0;
        }

        // Validation methods
        public async Task<bool> UsernameExistsAsync(string username)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = "SELECT COUNT(1) FROM accounts WHERE username = @Username;";
            var count = await dbConnection.QueryFirstOrDefaultAsync<int>(query, new { Username = username });

            return count > 0;
        }

        public async Task<bool> EmailExistsAsync(string email)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = "SELECT COUNT(1) FROM accounts WHERE email = @Email;";
            var count = await dbConnection.QueryFirstOrDefaultAsync<int>(query, new { Email = email });

            return count > 0;
        }

        public async Task<bool> EmailExistsAsync(string email, int excludeUserId)
        {
            using NpgsqlConnection dbConnection = new NpgsqlConnection(_connectionString);
            await dbConnection.OpenAsync();

            string query = "SELECT COUNT(1) FROM accounts WHERE email = @Email AND user_id != @UserId;";
            var count = await dbConnection.QueryFirstOrDefaultAsync<int>(query, new { Email = email, UserId = excludeUserId });

            return count > 0;
        }
    }
}
