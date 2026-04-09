from flask import Flask, render_template, request, jsonify, flash
import os
import json
import requests
import pyodbc
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Azure Key Vault configuration
KEY_VAULT_NAME = "mprkv2024az"
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"

def get_correios_auth_token():
    """Retrieves the base authentication token from Azure Key Vault.

    This function authenticates with Azure using DefaultAzureCredential and
    fetches the secret named "CorreiosAuthToken" from the specified Key Vault.

    Returns:
        str: The authentication token if found, otherwise None.
    """
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KV_URI, credential=credential)
        return client.get_secret("CorreiosAuthToken").value
    except Exception as e:
        print(f"Error retrieving secret from Key Vault: {e}")
        return None

def refresh_correios_token():
    """Refreshes the Correios API token and stores it as an environment variable.

    This function sends a POST request to the Correios authentication endpoint
    to get a new API token. If successful, it stores the token in the
    `CORREIOS_TOKEN` environment variable.

    Returns:
        str: The new token if the refresh is successful, otherwise None.
    """
    url = "https://api.correios.com.br/token/v1/autentica/contrato"
    auth_token = get_correios_auth_token()
    
    if not auth_token:
        print("Failed to retrieve authentication token from Key Vault")
        return None
        
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': auth_token
    }
    data = {
        "numero": "9912373734",
        "dr": 72
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()

        new_token = response_json.get('token')

        if new_token is None:
            print(f"Unexpected API response: {response_json}")
            raise ValueError("API did not return a token in the 'token' field.")

        os.environ['CORREIOS_TOKEN'] = new_token
        print("Token refreshed successfully!")
        return new_token

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing token: {e}")
        return None

def get_db_connection():
    """Establishes a connection to the SQL Server database.

    Connection parameters are retrieved from environment variables. If they are
    not set, it falls back to default values.

    Returns:
        pyodbc.Connection: A database connection object if successful, otherwise None.
    """
    try:
        # Database connection details
        db_server = os.environ.get("DB_SERVER")
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")

        conn_str = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={db_server};"
            f"Database={db_name};"
            f"Uid={db_user};"
            f"Pwd={db_password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout=30;"
        )

        conn = pyodbc.connect(conn_str, autocommit=True)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def search_cep_db(cep):
    """Searches for transportation information in the database by CEP.

    Args:
        cep (str): The CEP (postal code) to search for. It will be padded with
                   leading zeros to 8 digits.

    Returns:
        list[dict] | None: A list of dictionaries, where each dictionary
        represents a transport provider found for the CEP. Returns None if
        a database connection error occurs.
    """
    cep = cep.zfill(8)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor.execute(
            "SELECT DISTINCT Transportador FROM TransportTable WHERE ? BETWEEN CepInicial AND CepFinal ORDER BY Transportador ASC",
            cep
        )
        results = cursor.fetchall()
        
        # Convert results to list of dictionaries
        transport_data = []
        for result in results:
            transport_data.append({
                'transportador': result[0]
            })
        
        return transport_data
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def search_order_db(order):
    """Searches for order information in the database.

    Args:
        order (str): The order number to search for. It will be padded with
                     leading zeros to 8 digits.

    Returns:
        list[dict] | None: A list of dictionaries containing the destination CEP
        for the order. Returns None if a database connection error occurs.
    """
    # EXPLICANDO: Se for um pedido curto (ex: 123), preenchemos com zeros (00000123).
    # Se já for longo (como Mercado Livre), mantemos como está.
    if len(order) > 0 and len(order) < 8:
        order = order.zfill(8)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        # Use TOP 1 to stop scanning as soon as one match is found (faster for large tables)
        query = """
            SELECT TOP 1 
                DestCep, Transportadora, ServicoEntrega, Canal, 
                DestMunicipio, DestEstado, NomeProduto, DataVenda, ValorPedido 
            FROM PedidosDisponiveis 
            WHERE NumeroDoPedido = ?
        """
        cursor.execute(query, order)
        results = cursor.fetchall()
        
        # EXPLICANDO: Fallback para busca parcial (LIKE) caso a busca exata falhe.
        # Útil para lidar com números muito longos ou formatos variados (Mercado Livre).
        if not results:
            print(f"DEBUG: Busca exata falhou para {order}. Tentando LIKE...")
            like_query = query.replace("NumeroDoPedido = ?", "NumeroDoPedido LIKE ?")
            cursor.execute(like_query, f"%{order}%")
            results = cursor.fetchall()
        
        order_data = []
        for result in results:
            order_data.append({
                'cep_dest': result[0],
                'transportadora': result[1],
                'servico': result[2],
                'canal': result[3],
                'municipio': result[4],
                'estado': result[5],
                'produto': result[6],
                'data_venda': result[7],
                'valor': result[8]
            })
        
        return order_data
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def consultar_cep_correios(cep, token):
    """Queries CEP information using the Correios API.

    Args:
        cep (str): The CEP (postal code) to query.
        token (str): The bearer token for API authorization.

    Returns:
        dict | None: A dictionary containing the address information for the
        CEP if found, otherwise None.
    """
    url = f"https://api.correios.com.br/cep/v2/enderecos/{cep}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying CEP: {e}")
        return None

def validate_carrier_coverage(cep, carrier_name):
    """Checks if a specific carrier handles a given CEP.
    
    Args:
        cep (str): Target CEP.
        carrier_name (str): Name of the carrier to check.
        
    Returns:
        bool: True if coverage exists, False otherwise.
    """
    if not carrier_name:
        return False
        
    cep = str(cep).replace('-', '').replace(' ', '').zfill(8)

    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        # Simplified check for exact carrier or similar name
        query = """
            SELECT TOP 1 Transportador 
            FROM TransportTable 
            WHERE ? BETWEEN CepInicial AND CepFinal 
            AND Transportador LIKE ?
        """
        cursor.execute(query, (cep, f"%{carrier_name}%"))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Validation error: {e}")
        return False
    finally:
        conn.close()

@app.route('/')
def index():
    """Renders the main page of the web application.

    Returns:
        str: The rendered HTML of the index page.
    """
    return render_template('index.html')

@app.route('/search_cep', methods=['POST'])
def search_cep():
    """Handles the AJAX request for searching a CEP in the database.

    Expects a JSON payload with a 'cep' key.

    Returns:
        Response: A JSON response containing the search results or an error message.
    """
    try:
        data = request.get_json()
        cep = data.get('cep', '').strip()
        
        if not cep:
            return jsonify({'error': 'CEP field cannot be empty'}), 400
        
        if len(cep) != 8 or not cep.isdigit():
            return jsonify({'error': 'CEP must be 8 digits'}), 400
        
        results = search_cep_db(cep)
        
        if results is None:
            return jsonify({'error': 'Database connection error'}), 500
        
        if not results:
            return jsonify({'error': 'CEP not found'}), 404
        
        return jsonify({'results': results})
    
    except Exception as e:
        print(f"Error in search_cep: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/search_order', methods=['POST'])
def search_order():
    """Handles the AJAX request for searching an order in the database.

    Expects a JSON payload with an 'order' key.

    Returns:
        Response: A JSON response containing the search results or an error message.
    """
    try:
        data = request.get_json()
        order = data.get('order', '').strip()
        
        if not order:
            return jsonify({'error': 'Order field cannot be empty'}), 400
        
        results = search_order_db(order)
        
        if results is None:
            return jsonify({'error': 'Database connection error'}), 500
        
        if not results:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({'results': results})
    
    except Exception as e:
        print(f"Error in search_order: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/search_correios', methods=['POST'])
def search_correios():
    """Handles the AJAX request for searching a CEP using the Correios API.

    Expects a JSON payload with a 'cep' key. It will refresh the API token
    if necessary.

    Returns:
        Response: A JSON response containing the address data or an error message.
    """
    try:
        data = request.get_json()
        cep = data.get('cep', '').strip()
        
        if not cep:
            return jsonify({'error': 'CEP field cannot be empty'}), 400
        
        if len(cep) != 8 or not cep.isdigit():
            return jsonify({'error': 'CEP must be 8 digits'}), 400
        
        # Get or refresh token
        token = os.environ.get('CORREIOS_TOKEN')
        if not token:
            print("Token not available. Refreshing...")
            token = refresh_correios_token()
            if token is None:
                return jsonify({'error': 'Could not refresh the Correios token'}), 500
        
        # Query CEP
        dados_cep = consultar_cep_correios(cep, token)
        
        if dados_cep is None:
            return jsonify({'error': 'CEP not found or invalid'}), 404
        
        return jsonify({'results': dados_cep})
    
    except Exception as e:
        print(f"Error in search_correios: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/unified_search', methods=['POST'])
def unified_search():
    """Smart search that detects if input is CEP or Order.
    Also validates carrier coverage if it's an order.
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Campo de busca vazio'}), 400
            
        # 1. Detect if it's a CEP (8 digits)
        if len(query) == 8 and query.isdigit():
            # Search address (Correios)
            token = os.environ.get('CORREIOS_TOKEN') or refresh_correios_token()
            address = consultar_cep_correios(query, token)
            
            # Search carriers (Internal SQL)
            carriers = search_cep_db(query)
            
            # EXPLICANDO: Se a API dos Correios achou o endereço, injetamos os CORREIOS 
            # na lista de transportadoras sem precisar do SQL, mantendo a base leve.
            if address:
                carriers.insert(0, {'transportador': 'CORREIOS'})
            
            return jsonify({
                'type': 'cep',
                'address': address,
                'carriers': carriers
            })
            
        # 2. Treat as Order
        order_data = search_order_db(query)
        if not order_data:
            # Maybe it's a shorter CEP or invalid order?
            return jsonify({'error': 'Nenhum pedido ou CEP válido encontrado'}), 404
            
        order = order_data[0]
        # Cross-validation
        is_valid = validate_carrier_coverage(order['cep_dest'], order['transportadora'])
        
        return jsonify({
            'type': 'order',
            'order': order,
            'validation': {
                'is_valid_carrier': is_valid,
                'message': "Transportadora Válida" if is_valid else "⚠️ Transportadora não atende esta região!"
            }
        })
        
    except Exception as e:
        print(f"UI Error: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

@app.route('/health')
def health_check():
    """Provides a health check endpoint for monitoring.

    Returns:
        Response: A JSON response indicating the application status.
    """
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Initialize token on startup
    refresh_correios_token()
    app.run(host='0.0.0.0', port=8080, debug=False)
