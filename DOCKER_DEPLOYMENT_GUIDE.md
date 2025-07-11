# MPRConsultaCep Docker Deployment Guide

## ✅ Docker Implementation Complete!

Your PyQt6 desktop application has been successfully converted to a containerized web application. Here's what we've accomplished:

### 🎯 Conversion Summary

**From:** PyQt6 Desktop Application → **To:** Flask Web Application + Docker

### 📁 Files Created

1. **`app.py`** - Flask web server with REST API endpoints
2. **`templates/index.html`** - Modern web interface with same functionality
3. **`static/22994_boat_icon.ico`** - Application icon for web
4. **`Dockerfile`** - Container definition with production setup
5. **`docker-compose.yml`** - Multi-container deployment configuration
6. **`requirements-web.txt`** - Web application dependencies
7. **`start.sh`** - Production startup script with Gunicorn
8. **`.dockerignore`** - Optimized Docker build context
9. **`.env.template`** - Environment configuration template
10. **`deploy.bat`** - Windows deployment script
11. **`README.md`** - Comprehensive documentation

### 🚀 Quick Start

#### Option 1: Docker Compose (Recommended)
```bash
# 1. Configure environment
cp .env.template .env
# Edit .env with your Azure credentials

# 2. Deploy with one command
docker compose up -d

# 3. Access application
# http://localhost:8080
```

#### Option 2: Manual Docker
```bash
# Build image
docker build -t mpr-consulta-cep .

# Run container
docker run -d --name mpr-cep -p 8080:8080 \
  -e AZURE_CLIENT_ID=your-client-id \
  -e AZURE_CLIENT_SECRET=your-client-secret \
  -e AZURE_TENANT_ID=your-tenant-id \
  -e SECRET_KEY=your-secret-key \
  mpr-consulta-cep
```

#### Option 3: Windows Batch Script
```cmd
# Run the deployment script
deploy.bat
```

### 🔧 Current Status

✅ **Flask Web Application** - Running on port 8080  
✅ **Docker Image** - Built successfully with all dependencies  
✅ **Docker Compose** - Multi-container setup working  
✅ **Production Ready** - Gunicorn WSGI server with 4 workers  
✅ **Health Checks** - Built-in monitoring and restart capabilities  
✅ **Security** - Non-root user, environment variables for secrets  
✅ **Azure Integration** - Key Vault and SQL Server connectivity  

### 🌐 Web Interface Features

- **Order Search** - Find order information by order number
- **Correios CEP Search** - Official Brazilian postal API integration
- **Transport CEP Search** - Internal database transport lookup
- **Modern UI** - Responsive design with loading states and error handling
- **API Endpoints** - RESTful JSON API for all functionality

### 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │───▶│  Docker         │───▶│  Azure Services │
│   Port 8080     │    │  Flask + Python │    │  Key Vault +    │
│                 │    │  Gunicorn       │    │  SQL Server     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔐 Security Features

- **Azure Key Vault** integration for secret management
- **Environment variables** for configuration
- **Non-root container** execution
- **HTTPS ready** (add reverse proxy for SSL)
- **Health monitoring** with automatic restarts

### 📈 Production Deployment Options

1. **Azure Container Instances (ACI)**
   - Simple cloud deployment
   - Managed identity support
   - Pay-per-use pricing

2. **Azure App Service**
   - Platform-as-a-Service
   - Built-in scaling and monitoring
   - Easy CI/CD integration

3. **Azure Kubernetes Service (AKS)**
   - Enterprise container orchestration
   - Advanced scaling and management
   - Multi-environment support

4. **Self-Hosted Docker**
   - On-premises deployment
   - Full control over infrastructure
   - Cost-effective for stable workloads

### 🛠️ Management Commands

```bash
# View logs
docker compose logs -f

# Stop application
docker compose down

# Rebuild and restart
docker compose up -d --build

# Check container health
docker ps
docker inspect <container-id>

# Enter container for debugging
docker exec -it mpr-consulta-cep-web /bin/bash
```

### 📋 Environment Variables

Required for production deployment:

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_CLIENT_ID` | Azure service principal ID | Yes* |
| `AZURE_CLIENT_SECRET` | Azure service principal secret | Yes* |
| `AZURE_TENANT_ID` | Azure tenant ID | Yes* |
| `SECRET_KEY` | Flask session encryption key | Yes |
| `WORKERS` | Number of Gunicorn workers | No (default: 4) |
| `PORT` | Application port | No (default: 8080) |

*Not required when using Azure Managed Identity

### 🎉 Success Metrics

- ✅ Desktop app successfully converted to web app
- ✅ All original functionality preserved
- ✅ Modern, responsive web interface
- ✅ Production-ready Docker container
- ✅ Scalable architecture with load balancer support
- ✅ Secure configuration with Azure integration
- ✅ Comprehensive documentation and deployment guides

### 🔄 Next Steps

1. **Configure Azure credentials** in `.env` file
2. **Deploy to cloud** using your preferred Azure service
3. **Set up CI/CD pipeline** for automated deployments
4. **Configure monitoring** and logging solutions
5. **Set up SSL certificate** for HTTPS access
6. **Scale horizontally** by adding more container instances

Your application is now ready for production deployment! 🚀
