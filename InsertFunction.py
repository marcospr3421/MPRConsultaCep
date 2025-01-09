import pandas as pd
import pyodbc
from sqlalchemy import create_engine

def insert_xlsx_to_sql_table(file_path, table_name):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        #Establish connection using sqlalchemy for better error handling and efficiency.
        #Replace with your connection string.  Consider using environment variables for security.
        connection_string = "mssql+pyodbc://azureuser:Zaqmko21@@tcp:mprsqlserver.database.windows.net:1433/mprDB02?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
        engine = create_engine(connection_string)

        #More efficient to use pandas to_sql method for bulk inserts.
        df['cepInicial'] = df['cepInicial'].astype(str).str.zfill(8)
        df['cepFinal'] = df['cepFinal'].astype(str).str.zfill(8)

        df.to_sql(table_name, engine, if_exists='append', index=False)

        #Close the connection.  Engine manages this automatically in a `with` statement.
        engine.dispose()

        return True

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            print("Authentication error. Check your database credentials.")
        else:
            print(f"A pyodbc error occurred: {ex}")
        return False

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


#Example usage.  Remember to replace with your actual file path and table name.
file_path = r"C:\transport\Transportadoras.xlsx"
table_name = "TransportTable"

if insert_xlsx_to_sql_table(file_path, table_name):
    print(f"Data from '{file_path}' successfully inserted into table '{table_name}'.")
else:
    print(f"Data insertion failed.")

