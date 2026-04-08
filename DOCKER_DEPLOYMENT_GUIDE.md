# Web Application Deployment Guide

This guide provides detailed instructions for deploying the Flask web application using Docker and various Azure services.

## Docker Deployment

1.  **Build and run with Docker Compose**:
    ```bash
    # Set up your environment variables, for example in a .env file
    # AZURE_CLIENT_ID=your-client-id
    # AZURE_CLIENT_SECRET=your-client-secret
    # AZURE_TENANT_ID=your-tenant-id
    # SECRET_KEY=a-strong-secret-key

    # Build and run
    docker-compose up -d
    ```

2.  **Or build and run with Docker directly**:
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

## Azure Container Instance Deployment

1.  **Create Azure Container Instance**:

    ```bash
    az container create \
      --resource-group your-resource-group \
      --name mpr-consulta-cep \
      --image your-dockerhub-username/mpr-consulta-cep:latest \
      --dns-name-label mpr-consulta-cep \
      --ports 8080 \
      --environment-variables \
        AZURE_CLIENT_ID=your-client-id \
        AZURE_TENANT_ID=your-tenant-id \
        SECRET_KEY=your-secret-key \
      --secure-environment-variables \
        AZURE_CLIENT_SECRET=your-client-secret
    ```

## Azure App Service Deployment

1.  **Using Azure CLI**:
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
      --deployment-container-image-name your-dockerhub-username/mpr-consulta-cep:latest

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

## Security Considerations

- All sensitive configuration is stored in environment variables.
- Azure Key Vault is used for secret management.
- Database connections use encrypted connections.
- The application runs as a non-root user in the container.
- For production, consider configuring CORS and other security headers.

## Monitoring and Logging

- A health check endpoint is available at `/health`.
- Application logs are output to stdout/stderr.
- The container includes health checks for orchestration.
- Consider adding application monitoring (e.g., Application Insights).

## Troubleshooting

### Common Issues

1.  **Database Connection Failed**:
    - Check network connectivity to Azure SQL Server.
    - Verify credentials and firewall rules.
    - Ensure the ODBC driver is installed in the container.

2.  **Azure Key Vault Access Denied**:
    - Verify service principal credentials.
    - Check Key Vault access policies.
    - For managed identity, ensure it's enabled and has permissions.

3.  **Correios API Token Issues**:
    - Check if the token in Key Vault is valid.
    - Verify the token refresh logic is working.
    - Check for API rate limits.

### Logs

View application logs:
```bash
# Docker Compose
docker-compose logs -f mpr-consulta-cep

# Docker
docker logs -f mpr-consulta-cep-web
```