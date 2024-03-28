import requests
import pyodbc
import requests

def consult_cep(cep):
    # Connect to your SQL Server database
    conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=Zaqmko21@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the SQL query to retrieve the transport information based on the CEP
    cursor.execute(f"SELECT * FROM TransportTable WHERE '{cep}' BETWEEN CepInicial AND CepFinal")
    results = cursor.fetchall()
    # return results

    # # Fetch the result
    # result = cursor.fetchone()

    # Close the database connection
    conn.close()

    # If the result is found, return it
    if results:
        return results
    else:
        # If the result is not found, use the Postmon API as a fallback
        url = f"https://api.postmon.com.br/v1/cep/{cep}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

# Example usage
cep = input("Enter the CEP: ")
cep = cep.zfill(8)
results = consult_cep(cep)
if results:
    print(results)
else:
    print("CEP not found.")