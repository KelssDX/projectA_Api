using System;
using System.Net.Http;
using System.Threading.Tasks;
using Xunit;

namespace Affine.Tests.Helpers
{
    public class IntegrationTestBase : IClassFixture<AffineApiFactory>, IDisposable
    {
        protected readonly AffineApiFactory Factory;
        protected readonly HttpClient Client;

        public IntegrationTestBase(AffineApiFactory factory)
        {
            Factory = factory;
            Client = factory.CreateClient();
        }

        public void Dispose()
        {
            Client.Dispose();
        }
    }
} 