import requests
import pyodbc
    
    
def search_cep(self,main_window):
    cep = main_window.cep_input.text()
    cep = cep.zfill(8)
    
    # Connect to your SQL Server database
    conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=Zaqmko21@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()
    
    # Execute the SQL query to retrieve the transport information based on the CEP
    cursor.execute(f"SELECT * FROM TransportTable WHERE '{cep}' BETWEEN CepInicial AND CepFinal")
    results = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    # If the result is found, display it
    if results:
        self.result_label.setText(str(results))
        result_list = [f"Transport ID: {result[0]}, CEP Inicial: {result[1]}, CEP Final: {result[2]}, Cidade: {result[3]} Estado: {result[4]}, Transportador: {result[5]}" for result in results]
        self.result_label.setText("\n".join(result_list))
    else:
        # If the result is not found, use the Postmon API as a fallback
        url = f"https://api.postmon.com.br/v1/cep/{cep}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.result_label.setText(str(data))
        else:
            self.result_label.setText("CEP not found.")