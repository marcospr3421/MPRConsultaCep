import pandas as pd
import pyodbc

def insert_xlsx_to_sql_table(file_path, table_name):
    try:
        
        
        # Read the Excel file
        df = pd.read_excel(file_path)

        # Connect to your SQL Server database
        conn = pyodbc.connect("Driver={SQL Server};Server=tcp:mprsqlserver.database.windows.net,1433;Database=mprDB02;Uid=azureuser;Pwd=Zaqmko21@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Iterate over the DataFrame rows
        for index, row in df.iterrows():
            # Create the SQL query
            # Modify the cepInicial and cepFinal columns to include left-sided zeros
            row['cepInicial'] = str(row['cepInicial']).zfill(8)
            row['cepFinal'] = str(row['cepFinal']).zfill(8)

            # Create the SQL query
            query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['?'] * len(row))})"
            
            # Execute the SQL query
            cursor.execute(query, tuple(row))

            

        # Commit the transaction
        conn.commit()

        # Close the database connection
        conn.close()

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
insert_xlsx_to_sql_table(r"C:\transport\Transportadoras.xlsx", "TransportTable")