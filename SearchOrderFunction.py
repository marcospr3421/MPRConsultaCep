import pyodbc
import requests

def search_order(self,main_window):
    try:
        order = main_window.order_input.text()
        #order = order.zfill(20)
        # Connect to your SQL Server database
        conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=Zaqmko21@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Execute the SQL query to retrieve the transport information based on the order number
        cursor.execute("SELECT DestCep FROM PedidosDisponiveis WHERE NumeroDoPedido = ?", order)
        ordersResults = cursor.fetchone()
        if ordersResults is not None:
            dest_cep = ordersResults[0].replace('-', '')
            print(dest_cep)
            
            # Execute the SQL query to retrieve data from another table using the modified DestCep value
            cursor.execute(f"SELECT * FROM TransportTable WHERE '{dest_cep}' BETWEEN CepInicial AND CepFinal")
            ordersResults = cursor.fetchall()
            self.result_label_order.setText(str(ordersResults))
            result_list = [f"Cep: {dest_cep}, Cidade: {result[3]} Estado: {result[4]}, Transportador: {result[5]}" for result in ordersResults]
            self.result_label_order.setText("\n".join(result_list))
        else:
            # If the result is not found, use the Postmon API as a fallback
            url = f"https://api.postmon.com.br/v1/cep/{cep}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.result_label_cep.setText(str(data))
            else:
                self.result_label_cep.setText("CEP not found.")
            # another_results = cursor.fetchall()
            # another_results = [f"Transport ID: {another_results[0]}, Cidade: {another_results[3]} Estado: {another_results[4]}, Transportador: {another_results[5]}"]
            # self.result_label_order.setText("\n".join(str(result) for result in another_results))
            # for _ in another_results:
            #     if len(another_results) >= 6:
            #         another_results = [f"Transport ID: {another_results[0]}, Cidade: {another_results[3]} Estado: {another_results[4]}, Transportador: {another_results[5]}"]
                    
            #     else:
            #         print("another_results does not have enough elements")
        conn.close()
    except Exception as e:
        print(e)
        self.result_label_order.setText("An error occurred while searching for the order.")
        conn.close()
        return        






