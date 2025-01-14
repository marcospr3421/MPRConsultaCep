import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_excel('Transportadoras.xlsx')


# Create a list to store the insert statements
insert_statements = []

# Iterate over the DataFrame's rows
for index, row in df.iterrows():
    # Get the values for each column
    cep_inicial = row['cepInicial']
    cep_final = row['cepFinal']
    cidade = row['Cidade']
    uf = row['UF']
    transportador = row['Transportador']

    # Create the INSERT statement
    insert_statement = f"""
        INSERT INTO TransportTable (cepInicial, cepFinal, Cidade, UF, Transportador)
        VALUES ({cep_inicial}, {cep_final}, '{cidade}', '{uf}', '{transportador}');
    """

    # Append the INSERT statement to the list
    insert_statements.append(insert_statement)

# Print the list of INSERT statements
for insert_statement in insert_statements:
    print(insert_statement)