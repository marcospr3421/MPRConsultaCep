import pyodbc


def search_order(self,main_window):
    try:
        order = main_window.order_input.text()
        
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
            result_list = [f"CEP: {dest_cep} - CIDADE: {result[3]} - UF: {result[4]} - TRANSPORTE: {result[5]}" for result in ordersResults]
            self.result_label_order.setText("\n".join(result_list))
        else:
            # If the result is not found, display a message
            self.result_label_cep.setText("CEP not found.")
     
        conn.close()
    except Exception as e:
        print(e)
        self.result_label_order.setText("An error occurred while searching for the order.")
        conn.close()
        return        






