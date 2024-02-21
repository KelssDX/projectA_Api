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
        User GetByEmailAndPassword(string email, string password);
    }
}
