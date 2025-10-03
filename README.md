# MPR-CEP Consultation Tools

This repository contains a suite of tools for consulting Brazilian postal codes (CEP), transportation providers, and order information. The project includes a Flask web application, a PyQt6 desktop application, and several utility scripts.

## Project Overview

The main components of this project are:
-   **Flask Web Application**: A web-based interface for all search functionalities. It is containerized with Docker for easy deployment.
-   **PyQt6 Desktop Application**: A native desktop GUI for users who prefer a standalone application.
-   **Utility Scripts**: Tools for populating the database and testing API connectivity.

## Repository Structure

```
.
├── app.py                      # Core Flask web application
├── MprConsultaCep.py           # Core PyQt6 desktop application
├── SearchCepFunction.py        # Backend logic for CEP search (used by desktop app)
├── SearchOrderFunction.py      # Backend logic for order search (used by desktop app)
├── InsertFunction.py           # Utility to generate SQL INSERT statements from an Excel file
├── testeCep.py                 # CLI tool to test Correios CEP API
├── teste_app.py                # Unit tests for the Flask application
├── requirements.txt            # Dependencies for the desktop application and scripts
├── requirements-web.txt        # Dependencies for the Flask web application
├── Dockerfile                  # Docker configuration for the web app
├── DOCKER_DEPLOYMENT_GUIDE.md  # Detailed instructions for deploying the web app
└── README.md                   # This file
```

---

## Components

### 1. Flask Web Application

The web application (`app.py`) provides a browser-based interface for all search functions.

**Setup and Running Locally:**

1.  **Install dependencies**:
    ```bash
    pip install -r requirements-web.txt
    ```

2.  **Configure environment**:
    You will need to set up environment variables for Azure Key Vault access to allow the application to fetch the Correios API token. The required variables are `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID`.

3.  **Run the application**:
    ```bash
    python app.py
    ```
    The application will be available at `http://localhost:8080`.

**Deployment:**

For detailed instructions on how to deploy the web application using Docker, Azure Container Instances, or Azure App Service, please see [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md).

### 2. PyQt6 Desktop Application

The desktop application (`MprConsultaCep.py`) provides a native GUI for Windows, macOS, or Linux.

**Setup and Running:**

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the application**:
    ```bash
    python MprConsultaCep.py
    ```

### 3. Utility Scripts

-   **`InsertFunction.py`**:
    This script reads carrier data from `Transportadoras.xlsx` and generates SQL `INSERT` statements to populate the `TransportTable` in the database. To use it, simply run:
    ```bash
    python InsertFunction.py
    ```

-   **`testeCep.py`**:
    This is a command-line tool to quickly test the Correios CEP API. It will prompt you to enter a CEP and will print the results.
    ```bash
    python testeCep.py
    ```

---

## Testing

The repository includes a unit test file for the Flask application.

-   **`teste_app.py`**: Contains unit tests for the database connection logic in `app.py`. To run the tests:
    ```bash
    python -m unittest teste_app.py
    ```

---

## Database

The applications connect to a SQL Server database with the following key tables:

-   `TransportTable`: Stores CEP ranges and their corresponding transportation providers.
-   `PedidosDisponiveis`: Stores order numbers and their destination CEPs.

The connection string is configured within the application files and can be modified to point to a different database instance.