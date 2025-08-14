from flask import Flask, render_template, request, jsonify, flash
import os
import json
import requests
import pyodbc
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Azure Key Vault configuration
KEY_VAULT_NAME = "mprkv2024az"
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"

def get_correios_auth_token():
    """Get the base authentication token from Azure Key Vault"""
    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KV_URI, credential=credential)
        return client.get_secret("CorreiosAuthToken").value
    except Exception as e:
        print(f"Error retrieving secret from Key Vault: {e}")
        return None

def refresh_correios_token():
    """Refresh the Correios API token"""
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
    """Get database connection"""
    try:
        conn = pyodbc.connect(
            "Driver={ODBC Driver 18 for SQL Server};"
            "Server=tcp:mprsqlserver.database.windows.net,1433;"
            "Database=mprDB02;"
            "Uid=azureuser;"
            "Pwd=GMNh*DfrdzmFkAZD*UfQq9uix;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def search_cep_db(cep):
    """Search for transport information by CEP"""
    cep = cep.zfill(8)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM TransportTable WHERE ? BETWEEN CepInicial AND CepFinal ORDER BY Transportador ASC",
            cep
        )
        results = cursor.fetchall()
        
        # Convert results to list of dictionaries
        transport_data = []
        for result in results:
            transport_data.append({
                'cep_inicial': result[1],
                'cep_final': result[2],
                'cidade': result[3],
                'uf': result[4],
                'transportador': result[5]
            })
        
        return transport_data
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def search_order_db(order):
    """Search for order information"""
    order = order.zfill(8)
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DestCep FROM PedidosDisponiveis WHERE NumeroDoPedido = ?", order)
        results = cursor.fetchall()
        
        order_data = []
        for result in results:
            order_data.append({
                'cep_dest': result[0]
            })
        
        return order_data
    except Exception as e:
        print(f"Database query error: {e}")
        return None
    finally:
        conn.close()

def consultar_cep_correios(cep, token):
    """Query CEP information using Correios API"""
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

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/search_cep', methods=['POST'])
def search_cep():
    """Handle CEP search for transport companies"""
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
    """Handle order search"""
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
    """Handle Correios CEP search"""
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Initialize token on startup
    refresh_correios_token()
    app.run(host='0.0.0.0', port=8080, debug=False)
