# Risk Assessment App Frontend

This is the frontend application for the Risk Assessment system, built with Python and Flet framework. The application now includes full integration with the backend APIs.

## Features

- **User authentication** via Identity API
- **Risk assessment operations** via Auditing API
- **Interactive dashboards** with real-time data
- **Department and project management**
- **Report generation** (PDF and Excel)
- **Risk visualization** and heatmaps
- **Control testing workflows**

## Technology Stack

- **Python**: Core programming language
- **Flet**: Cross-platform GUI framework
- **aiohttp**: Async HTTP client for API integration
- **PostgreSQL**: Database (fallback for direct access)
- **ReportLab**: PDF generation
- **OpenPyXL**: Excel export functionality
- **Pandas**: Data processing

## Backend API Integration

The frontend integrates with two main backend APIs:

### Identity API (Affina.Identity.API)
- **Authentication endpoint**: `GET /api/v1/UserLogin/Login`
- **Purpose**: User login and authentication
- **Port**: 7001 (default)

### Auditing API (Affine.Auditing.API)
- **Risk Assessment endpoints**: Various CRUD operations
- **Lookup data endpoints**: Risks, controls, outcomes, etc.
- **Heatmap endpoint**: Risk visualization data
- **Purpose**: Core risk assessment functionality
- **Port**: 7000 (default)

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Backend APIs running (Affina.Identity.API and Affine.Auditing.API)
- Network access to the API endpoints

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd RiskAssessmentApp_Frontend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Update API endpoints** in `config.py`:
   ```python
   API_CONFIG = {
       "auditing_api": "https://localhost:7000/api/v1",  # Your Auditing API URL
       "identity_api": "https://localhost:7001/api/v1",  # Your Identity API URL
       "timeout": 30,
       "verify_ssl": False  # Set to True in production
   }
   ```

2. **Test API connectivity**:
   ```bash
   python test_api_integration.py
   ```

### Running the Application

#### Quick Start (Windows)
```bash
start_frontend.bat
```

#### Quick Start (macOS/Linux)
```bash
./start_frontend.sh
```

#### Manual Start
```bash
python main.py
```

## API Integration Details

### Authentication Flow
1. User enters email and password in the frontend
2. Frontend calls Identity API: `GET /api/v1/UserLogin/Login?email=...&password=...`
3. On successful authentication, user data is stored in the frontend
4. Fallback to local database if API is unavailable

### Risk Assessment Operations
The frontend now uses the actual backend API endpoints:

- **Get Risk Assessment**: `GET /api/v1/RiskAssessment/GetRiskAssessment?referenceId=...`
- **Create Risk Assessment**: `POST /api/v1/RiskAssessment/CreateRiskAssessment`
- **Update Risk Assessment**: `PUT /api/v1/RiskAssessment/UpdateRiskAssessment/{referenceId}`
- **Get Heatmap Data**: `GET /api/v1/RiskGraphs/GetHeatmap?referenceId=...`

### Lookup Data
All dropdown and selection data is fetched from the API:
- Risks, Controls, Outcomes
- Risk Likelihoods, Impacts
- Risk Categories, Evidence types
- Data Frequencies, etc.

## Testing

### API Integration Test
Run the test script to verify connectivity:
```bash
python test_api_integration.py
```

This will test:
- ✅ Identity API authentication
- ✅ Auditing API endpoints
- ✅ Data retrieval operations
- ✅ Reference creation

### Expected Test Results
- **Identity API**: Should authenticate with valid credentials
- **Auditing API**: Should return data from lookup endpoints
- **Error Handling**: Graceful fallback when APIs are unavailable

## Project Structure

```
RiskAssessmentApp_Frontend/
├── main.py                    # Main application entry point
├── config.py                  # API configuration and endpoints
├── test_api_integration.py    # API integration test script
├── api/                       # API integration layer
│   ├── identity_client.py     # Identity API client
│   ├── auditing_client.py     # Auditing API client
│   └── risk_calculator.py     # Risk calculation utilities
├── controllers/               # Business logic controllers
│   ├── auth_controller.py     # Updated for Identity API
│   ├── assessment_controller.py # Updated for Auditing API
│   └── ...
├── views/                     # UI components
├── models/                    # Data models
├── utils/                     # Utility functions
└── requirements.txt           # Python dependencies
```

## Development & Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure backend APIs are running on the configured ports
   - Check SSL certificate settings (`verify_ssl` in config)
   - Verify network connectivity to API endpoints

2. **Authentication Failures**
   - Verify user credentials exist in the backend system
   - Check Identity API is responding on the correct port
   - Review API logs for authentication errors

3. **Data Loading Issues**
   - Run the API integration test to diagnose specific endpoints
   - Check Auditing API database connection
   - Verify API controllers are properly configured

### Debugging

1. **Enable verbose logging** by adding print statements in API clients
2. **Use the test script** to isolate API issues
3. **Check backend API logs** for server-side errors
4. **Monitor network traffic** if connection issues persist

### Development Notes

- The application uses async/await for all API calls
- Graceful fallback to database when APIs are unavailable
- All API clients use context managers for proper resource cleanup
- Authentication state is managed in the auth controller
- API responses are cached where appropriate for performance

## Production Deployment

For production deployment:

1. **Update SSL settings**: Set `verify_ssl = True` in config
2. **Use production API URLs**: Update endpoints in config
3. **Secure credentials**: Use environment variables for sensitive data
4. **Enable logging**: Configure proper logging for production monitoring
5. **Error handling**: Ensure robust error handling for network issues

## Contributing

1. Follow the existing code patterns for API integration
2. Add tests for new API endpoints
3. Update the integration test script for new features
4. Maintain backward compatibility with fallback database access
5. Document any new API dependencies 