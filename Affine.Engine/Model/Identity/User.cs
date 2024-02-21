using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Identity
{
    public class User
    {
        public int Id { get; set; }
        public string Email { get; set; }
        public string Password { get; set; }
        public int UserTypeId { get; set; } 
        public UserType UserType { get; set; }
    }

    public class UserType
    {
        public int Id { get; set; }
        public string Type { get; set; }
    }
}
