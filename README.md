# MPRConsultaCep Web Application

A web application for Brazilian postal code (CEP) and transport information lookup, converted from a PyQt6 desktop application to a Flask web application with Docker support.

## Features

- **Order Search**: Search for order information by order number
- **Correios CEP Search**: Query Brazilian postal addresses using the official Correios API
- **Transport Search**: Find transport companies by postal code using internal database
- **Azure Integration**: Secure token management using Azure Key Vault
- **Docker Support**: Containerized deployment ready for production

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Azure Key Vault with Correios authentication token
- Azure service principal or managed identity for Key Vault access

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd MPRConsultaCep
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements-web.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your Azure credentials
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser to `http://localhost:8080`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   # Copy and configure environment variables
   cp .env.template .env
   # Edit .env with your Azure configuration
   
   # Build and run
   docker-compose up -d
   ```

2. **Or build and run with Docker directly**:
   ```bash
   # Build the image
   docker build -t mpr-consulta-cep .
   
   # Run the container
   docker run -d \
     --name mpr-consulta-cep-web \
     -p 8080:8080 \
     -e AZURE_CLIENT_ID=your-client-id \
     -e AZURE_CLIENT_SECRET=your-client-secret \
     -e AZURE_TENANT_ID=your-tenant-id \
     -e SECRET_KEY=your-secret-key \
     mpr-consulta-cep
   ```

### Azure Container Instance Deployment

1. **Create Azure Container Instance**:

   ```bash
   az container create \
     --resource-group your-resource-group \
     --name mpr-consulta-cep \
     --image your-registry/mpr-consulta-cep:latest \
     --dns-name-label mpr-consulta-cep \
     --ports 8080 \
     --environment-variables \
       AZURE_CLIENT_ID=your-client-id \
       AZURE_TENANT_ID=your-tenant-id \
       SECRET_KEY=your-secret-key \
     --secure-environment-variables \
       AZURE_CLIENT_SECRET=your-client-secret
   ```

### Azure App Service Deployment

1. **Using Azure CLI**:
   ```bash
   # Create App Service Plan
   az appservice plan create \
     --name mpr-consulta-cep-plan \
     --resource-group your-resource-group \
     --sku B1 \
     --is-linux
   
   # Create Web App
   az webapp create \
     --resource-group your-resource-group \
     --plan mpr-consulta-cep-plan \
     --name mpr-consulta-cep-app \
     --deployment-container-image-name your-registry/mpr-consulta-cep:latest
   
   # Configure environment variables
   az webapp config appsettings set \
     --resource-group your-resource-group \
     --name mpr-consulta-cep-app \
     --settings \
       AZURE_CLIENT_ID=your-client-id \
       AZURE_CLIENT_SECRET=your-client-secret \
       AZURE_TENANT_ID=your-tenant-id \
       SECRET_KEY=your-secret-key \
       WEBSITES_PORT=8080
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_CLIENT_ID` | Azure service principal client ID | Yes* |
| `AZURE_CLIENT_SECRET` | Azure service principal client secret | Yes* |
| `AZURE_TENANT_ID` | Azure tenant ID | Yes* |
| `AZURE_USE_MSI` | Use managed identity instead of service principal | No |
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `FLASK_ENV` | Flask environment (development/production) | No |
| `WORKERS` | Number of Gunicorn workers | No |
| `PORT` | Application port | No |
| `HOST` | Application host | No |

*Not required when using managed identity (`AZURE_USE_MSI=true`)

### Azure Key Vault Setup

1. Create a Key Vault in Azure
2. Store your Correios authentication token as a secret named `CorreiosAuthToken`
3. Grant your service principal or managed identity access to the Key Vault

### Database Configuration

The application uses SQL Server on Azure with the following connection details:
- Server: `mprsqlserver.database.windows.net`
- Database: `mprDB02`
- Tables: `TransportTable`, `PedidosDisponiveis`

## API Endpoints

- `GET /` - Main application page
- `POST /search_cep` - Search transport companies by CEP
- `POST /search_order` - Search order information
- `POST /search_correios` - Search Correios address information
- `GET /health` - Health check endpoint

## Architecture

The application is structured as follows:

```
MPRConsultaCep/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── static/
│   └── 22994_boat_icon.ico
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container deployment
├── start.sh             # Production startup script
├── requirements-web.txt  # Python dependencies
├── .env.template        # Environment variables template
└── README.md           # This file
```

## Security Considerations

- All sensitive configuration is stored in environment variables
- Azure Key Vault is used for secret management
- Database connections use encrypted connections
- Application runs as non-root user in container
- CORS and other security headers should be configured for production

## Monitoring and Logging

- Health check endpoint available at `/health`
- Application logs are output to stdout/stderr
- Container includes health checks for orchestration
- Consider adding application monitoring (Application Insights, etc.)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check network connectivity to Azure SQL Server
   - Verify credentials and firewall rules
   - Ensure ODBC driver is installed in container

2. **Azure Key Vault Access Denied**:
   - Verify service principal credentials
   - Check Key Vault access policies
   - For managed identity, ensure it's enabled and has permissions

3. **Correios API Token Issues**:
   - Check if token in Key Vault is valid
   - Verify token refresh logic is working
   - Check API rate limits

### Logs

View application logs:
```bash
# Docker Compose
docker-compose logs -f mpr-consulta-cep

# Docker
docker logs -f mpr-consulta-cep-web
```

## Development

### Project Structure Migration

This web application was converted from a PyQt6 desktop application with the following mappings:

- `MprConsultaCep.py` → `app.py` (Flask web server)
- PyQt6 UI → `templates/index.html` (Web interface)
- Dialog windows → JSON API responses
- Desktop widgets → HTML forms and JavaScript

### Adding New Features

1. Add new routes in `app.py`
2. Update the frontend in `templates/index.html`
3. Test locally before building Docker image
4. Update this README with new configuration options

## License

[Add your license information here]
