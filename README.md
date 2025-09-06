# Elsa Studio v3 - .NET 8

This project contains a complete Elsa Studio v3 implementation targeting .NET 8.

## Prerequisites

- .NET 8 SDK
- PostgreSQL database server
- Node.js (for building frontend assets if needed)

## Projects

### ElsaStudio
A Blazor WebAssembly application that provides the visual workflow designer interface.

**Features:**
- Visual workflow designer
- Workflow management
- User authentication
- Modern UI with MudBlazor components

### ElsaServer
A .NET 8 Web API that serves as the Elsa workflow engine backend.

**Features:**
- Workflow execution engine
- REST API endpoints
- PostgreSQL database integration
- CORS configuration for Studio access

## Getting Started

### 1. Database Setup
Make sure PostgreSQL is running and create a database named `elsa`:

```sql
CREATE DATABASE elsa;
```

Update the connection string in `ElsaServer/appsettings.json` if needed:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=elsa;Username=postgres;Password=password"
  }
}
```

### 2. Running the Applications

#### Start the Elsa Server (Backend)
```bash
cd ElsaServer
dotnet run
```

The server will start on `https://localhost:5001`

#### Start the Elsa Studio (Frontend)
```bash
dotnet run --project ElsaStudio.csproj
```

The studio will start on `https://localhost:7001`

### 3. Access the Application

Open your browser and navigate to `https://localhost:7001` to access the Elsa Studio interface.

## Configuration

### ElsaStudio Configuration
- **appsettings.json**: Contains the Elsa Server URL configuration
- **Properties/launchSettings.json**: Development server settings

### ElsaServer Configuration
- **appsettings.json**: Database connection and logging settings
- **Program.cs**: Elsa services and middleware configuration

## Package Versions

All projects use Elsa v3.4.0 packages:
- Elsa.Studio v3.4.0
- Elsa.Studio.Core v3.4.0
- Elsa.Studio.Workflows v3.4.0
- Elsa.Studio.Workflows.Designer v3.4.0
- MudBlazor v6.19.1

## Troubleshooting

1. **CORS Issues**: Make sure the ElsaServer is running and CORS is properly configured
2. **Database Connection**: Verify PostgreSQL is running and connection string is correct
3. **Package Restore**: Run `dotnet restore` if you encounter package issues

## Development

To make changes to the Studio:
1. Modify the Blazor components in the ElsaStudio project
2. Update the backend API in the ElsaServer project
3. Both projects support hot reload during development 

# ProjectA API - Risk Assessment System

This is a comprehensive risk assessment system with multiple components including backend APIs, workflow engines, and a Python-based frontend application.

## Architecture Overview

The system consists of:

1. **Backend APIs** (.NET 8)
   - Identity Management API
   - Risk Assessment API
   - Auditing API
   
2. **Workflow Engines** (Elsa Studio v3)
   - Workflow Server
   - Workflow Studio
   
3. **Frontend Application** (Python + Flet)
   - Risk Assessment Desktop Application
   - Interactive dashboards and reporting

## Projects

### Backend APIs

#### Affina.Identity.API
User authentication and identity management service.

#### Affine.Auditing.API  
Main risk assessment API with controllers for:
- Risk assessments
- Risk graphs and heatmaps
- Auditing workflows

#### Affine.Engine
Core business logic and data models shared across APIs.

### Workflow Management

#### Affine.Auditing.Workflows.Server
Elsa workflow engine server for auditing processes.

#### Affine.Auditing.Workflows.Studio
Blazor WebAssembly application for visual workflow design.

### Frontend Application

#### RiskAssessmentApp_Frontend
A Python-based desktop application built with Flet framework providing:
- User authentication
- Risk assessment creation and management
- Interactive dashboards
- Report generation (PDF/Excel)
- Department and project management

**Technology Stack:**
- Python 3.8+
- Flet (Cross-platform GUI framework)
- PostgreSQL integration
- ReportLab for PDF generation
- OpenPyXL for Excel exports

## Getting Started

### Prerequisites

- .NET 8 SDK
- PostgreSQL database server
- Python 3.8+ (for frontend)
- Node.js (for building frontend assets if needed)

### Backend Setup

1. **Database Setup**
   ```sql
   CREATE DATABASE risk_assessment;
   ```

2. **Update Connection Strings**
   Update connection strings in `appsettings.json` files across projects.

3. **Run Backend Services**
   ```bash
   # Start Identity API
   dotnet run --project Affina.Identity.API
   
   # Start Auditing API
   dotnet run --project Affine.Auditing.API
   
   # Start Workflow Server
   dotnet run --project Affine.Auditing.Workflows.Server
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd RiskAssessmentApp_Frontend
   ```

2. **Setup Python Environment**
   ```bash
   # Windows
   start_frontend.bat
   
   # macOS/Linux
   ./start_frontend.sh
   ```

3. **Manual Setup (Alternative)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

## Configuration

### API Configuration
- Update `appsettings.json` files with correct database connections
- Configure CORS settings for frontend access

### Frontend Configuration
- Update `config.py` with correct API endpoints
- Configure database connection if direct DB access is needed

## Development

### Running Tests
```bash
dotnet test Affine.Tests
```

### API Documentation
APIs support OpenAPI/Swagger documentation available at:
- Identity API: `https://localhost:7001/swagger`
- Auditing API: `https://localhost:7000/swagger`

## Project Structure

```
projectA_Api/
├── Affina.Identity.API/          # Identity management API
├── Affine.Auditing.API/          # Main auditing API
├── Affine.Engine/                # Shared business logic
├── Affine.Tests/                 # Unit and integration tests
├── Affine.Auditing.Workflows.*/  # Workflow management
├── RiskAssessmentApp_Frontend/   # Python frontend application
└── ElsaServer/                   # Additional workflow server
```

## Troubleshooting

1. **CORS Issues**: Ensure APIs are running and CORS is configured for frontend access
2. **Database Connection**: Verify PostgreSQL is running with correct credentials
3. **Python Dependencies**: Use virtual environment and install from requirements.txt
4. **API Endpoints**: Update frontend config.py with correct API URLs

## Contributing

1. Follow the coding standards defined in the project
2. Add unit tests for new features
3. Update documentation as needed
4. Use the existing project structure and patterns 