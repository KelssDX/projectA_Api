"""
Example usage of the API clients for common risk assessment operations.
This script demonstrates how to use the Identity and Auditing API clients.
"""

import asyncio
from api.identity_client import IdentityAPIClient
from api.auditing_client import AuditingAPIClient


async def example_authentication():
    """Example: User authentication with Identity API"""
    print("=== Authentication Example ===")
    
    async with IdentityAPIClient() as identity_client:
        try:
            # Authenticate user
            user_data = await identity_client.login("admin@example.com", "admin")
            print(f"User authenticated: {user_data.get('email', 'Unknown')}")
            print(f"User type: {user_data.get('userType', 'Unknown')}")
            return user_data
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None


async def example_risk_data_fetching():
    """Example: Fetching lookup data from Auditing API"""
    print("\n=== Risk Data Fetching Example ===")
    
    async with AuditingAPIClient() as auditing_client:
        try:
            # Fetch various lookup data
            print("Fetching risks...")
            risks = await auditing_client.get_risks()
            print(f"Found {len(risks) if risks else 0} risks")
            
            print("Fetching controls...")
            controls = await auditing_client.get_controls()
            print(f"Found {len(controls) if controls else 0} controls")
            
            print("Fetching risk likelihoods...")
            likelihoods = await auditing_client.get_risk_likelihoods()
            print(f"Found {len(likelihoods) if likelihoods else 0} risk likelihoods")
            
            return {
                "risks": risks,
                "controls": controls,
                "likelihoods": likelihoods
            }
            
        except Exception as e:
            print(f"Failed to fetch risk data: {e}")
            return None


async def example_create_reference():
    """Example: Creating a risk assessment reference"""
    print("\n=== Create Reference Example ===")
    
    async with AuditingAPIClient() as auditing_client:
        try:
            # Sample reference data (adjust structure based on your backend model)
            reference_data = {
                "title": "Sample Risk Assessment 2024",
                "description": "Example risk assessment for demonstration",
                "department": "IT Department",
                "auditor": "Demo User",
                "status": "Draft"
            }
            
            print("Creating risk assessment reference...")
            result = await auditing_client.create_reference(reference_data)
            
            if result:
                reference_id = result.get("referenceId")
                print(f"Reference created successfully! ID: {reference_id}")
                return reference_id
            else:
                print("Failed to create reference")
                return None
                
        except Exception as e:
            print(f"Error creating reference: {e}")
            return None


async def example_create_risk_assessment(reference_id):
    """Example: Creating a risk assessment with data"""
    print("\n=== Create Risk Assessment Example ===")
    
    if not reference_id:
        print("No reference ID available, skipping risk assessment creation")
        return None
    
    async with AuditingAPIClient() as auditing_client:
        try:
            # Sample risk assessment data (adjust structure based on your backend model)
            assessment_data = {
                "assessments": [
                    {
                        "riskId": 1,
                        "likelihoodId": 1,
                        "impactId": 1,
                        "controlId": 1,
                        "description": "Sample risk assessment item",
                        "mitigationPlan": "Implement additional controls"
                    }
                ],
                "reference": None,  # Using existing reference
                "referenceId": reference_id
            }
            
            print(f"Creating risk assessment for reference {reference_id}...")
            result = await auditing_client.create_risk_assessment(assessment_data)
            
            if result:
                print("Risk assessment created successfully!")
                return result
            else:
                print("Failed to create risk assessment")
                return None
                
        except Exception as e:
            print(f"Error creating risk assessment: {e}")
            return None


async def example_get_heatmap(reference_id):
    """Example: Getting heatmap data for visualization"""
    print("\n=== Get Heatmap Example ===")
    
    if not reference_id:
        print("No reference ID available, skipping heatmap retrieval")
        return None
    
    async with AuditingAPIClient() as auditing_client:
        try:
            print(f"Fetching heatmap data for reference {reference_id}...")
            heatmap_data = await auditing_client.get_heatmap(reference_id)
            
            if heatmap_data:
                print("Heatmap data retrieved successfully!")
                print(f"Data type: {type(heatmap_data)}")
                return heatmap_data
            else:
                print("No heatmap data found (this is normal for new assessments)")
                return None
                
        except Exception as e:
            print(f"Error fetching heatmap: {e}")
            return None


async def main():
    """Main example demonstrating the complete workflow"""
    print("🚀 Risk Assessment API Usage Examples")
    print("=" * 50)
    
    # Step 1: Authentication
    user = await example_authentication()
    
    # Step 2: Fetch reference data
    risk_data = await example_risk_data_fetching()
    
    # Step 3: Create a reference
    reference_id = await example_create_reference()
    
    # Step 4: Create risk assessment (if reference was created)
    if reference_id:
        assessment = await example_create_risk_assessment(reference_id)
        
        # Step 5: Get heatmap data
        heatmap = await example_get_heatmap(reference_id)
    
    print("\n" + "=" * 50)
    print("✅ API Usage Examples Complete!")
    print("\nThis demonstrates the basic workflow:")
    print("1. Authenticate user via Identity API")
    print("2. Fetch lookup data via Auditing API")
    print("3. Create risk assessment reference")
    print("4. Create risk assessment with data")
    print("5. Retrieve visualization data")


if __name__ == "__main__":
    asyncio.run(main()) 