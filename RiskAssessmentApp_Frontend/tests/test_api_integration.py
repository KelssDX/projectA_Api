"""
Test script for API integration with backend services.
Run this script to verify that the frontend can communicate with the backend APIs.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.identity_client import IdentityAPIClient
from api.auditing_client import AuditingAPIClient


async def test_identity_api():
    """Test the Identity API connection and authentication"""
    print("🔑 Testing Identity API...")
    
    async with IdentityAPIClient() as client:
        try:
            # Test with demo credentials
            print("  Attempting login with demo credentials...")
            user_data = await client.login("admin@example.com", "admin")
            print(f"  ✅ Login successful! User data: {user_data}")
            return True
            
        except Exception as e:
            print(f"  ❌ Login failed: {str(e)}")
            return False


async def test_auditing_api():
    """Test the Auditing API connection and basic endpoints"""
    print("\n📊 Testing Auditing API...")
    
    async with AuditingAPIClient() as client:
        success_count = 0
        total_tests = 0
        
        # Test endpoints that don't require parameters
        endpoints_to_test = [
            ("get_risks", "Get Risks"),
            ("get_controls", "Get Controls"),
            ("get_outcomes", "Get Outcomes"),
            ("get_risk_likelihoods", "Get Risk Likelihoods"),
            ("get_impacts", "Get Impacts"),
            ("get_key_secondary_risks", "Get Key Secondary Risks"),
            ("get_risk_categories", "Get Risk Categories"),
            ("get_data_frequencies", "Get Data Frequencies"),
            ("get_outcome_likelihoods", "Get Outcome Likelihoods"),
            ("get_evidence", "Get Evidence")
        ]
        
        for endpoint_method, description in endpoints_to_test:
            total_tests += 1
            try:
                print(f"  Testing {description}...")
                method = getattr(client, endpoint_method)
                result = await method()
                
                if result is not None:
                    print(f"    ✅ {description} - Success (returned {type(result).__name__})")
                    success_count += 1
                else:
                    print(f"    ⚠️  {description} - No data returned")
                    
            except Exception as e:
                print(f"    ❌ {description} - Error: {str(e)}")
        
        # Test endpoints that require parameters (with error handling)
        print("  Testing parameterized endpoints...")
        
        # Test get_risk_assessment with a sample ID
        total_tests += 1
        try:
            result = await client.get_risk_assessment(1)
            if result:
                print("    ✅ Get Risk Assessment - Success")
                success_count += 1
            else:
                print("    ⚠️  Get Risk Assessment - No data for ID 1 (expected)")
                success_count += 1  # This is expected behavior
        except Exception as e:
            print(f"    ❌ Get Risk Assessment - Error: {str(e)}")
        
        # Test get_heatmap with a sample ID
        total_tests += 1
        try:
            result = await client.get_heatmap(1)
            if result:
                print("    ✅ Get Heatmap - Success")
                success_count += 1
            else:
                print("    ⚠️  Get Heatmap - No data for ID 1 (expected)")
                success_count += 1  # This is expected behavior
        except Exception as e:
            print(f"    ❌ Get Heatmap - Error: {str(e)}")
        
        print(f"\n  📈 Auditing API Results: {success_count}/{total_tests} tests passed")
        return success_count > 0


async def test_create_reference():
    """Test creating a risk assessment reference"""
    print("\n📝 Testing Risk Assessment Reference Creation...")
    
    async with AuditingAPIClient() as client:
        try:
            # Sample reference data
            reference_data = {
                "title": "Test Risk Assessment",
                "description": "API Integration Test",
                "department": "IT",
                "auditor": "Test User",
                "created_date": "2024-01-01T00:00:00Z"
            }
            
            print("  Creating test reference...")
            result = await client.create_reference(reference_data)
            
            if result:
                print(f"    ✅ Reference created successfully: {result}")
                return True
            else:
                print("    ❌ Failed to create reference")
                return False
                
        except Exception as e:
            print(f"    ❌ Error creating reference: {str(e)}")
            return False


async def main():
    """Run all API integration tests"""
    print("🚀 Starting API Integration Tests")
    print("=" * 50)
    
    # Test Identity API
    identity_success = await test_identity_api()
    
    # Test Auditing API
    auditing_success = await test_auditing_api()
    
    # Test creation endpoint
    creation_success = await test_create_reference()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  Identity API: {'✅ PASS' if identity_success else '❌ FAIL'}")
    print(f"  Auditing API: {'✅ PASS' if auditing_success else '❌ FAIL'}")
    print(f"  Creation Test: {'✅ PASS' if creation_success else '❌ FAIL'}")
    
    if identity_success and auditing_success:
        print("\n🎉 All core API tests passed! Your frontend is ready to use the backend APIs.")
    else:
        print("\n⚠️  Some tests failed. Check that your backend APIs are running:")
        print("     - Identity API: https://localhost:7001")
        print("     - Auditing API: https://localhost:7000")
        
    return identity_success and auditing_success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1) 