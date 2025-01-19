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
    public class UserRepository: IUserRepository
    {
        private readonly string _connectionString;

        public UserRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        public User GetByEmailAndPassword(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string query = @"
                             SELECT * FROM accounts 
                             WHERE email = @Email AND password = @Password;";

            return dbConnection.QueryFirstOrDefault<User>(query, new { Email = email, Password = password });
        }
    }
}
