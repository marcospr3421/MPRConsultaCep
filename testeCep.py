"""
Provides a function to query the Correios CEP API and a CLI for testing.

This script contains the `consultar_cep` function, which is used by the main
PyQt6 application to fetch address data. It can also be run as a standalone
script to test the API query functionality from the command line.
"""
import requests
import os

def consultar_cep(cep, token):
  """
  Queries CEP information using the Correios API.

  Args:
    cep (str): The CEP (postal code) to query, consisting of numbers only.
    token (str): The access token for the Correios API.

  Returns:
    dict | None: A dictionary with the CEP information if the query is
                 successful, otherwise None.
  """

  url = f"https://api.correios.com.br/cep/v2/enderecos/{cep}"
  headers = {
      "Authorization": f"Bearer {token}"
  }

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an exception for HTTP error codes
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f"Error querying CEP: {e}")
    return None

def main():
  """
  Main function to run the script from the command line.

  Prompts the user for a CEP. The API token is retrieved from the
  `CORREIOS_API_TOKEN` environment variable or prompted if not set.
  """

  cep = input("Digite o CEP (apenas números): ")
  token = os.environ.get("CORREIOS_API_TOKEN")

  if not token:
      token = input("Please enter your Correios API token: ")

  if not token:
      print("An API token must be provided via CORREIOS_API_TOKEN environment variable or user input.")
      return

  dados_cep = consultar_cep(cep, token)

  if dados_cep:
    print("\nInformações do CEP:")
    for chave, valor in dados_cep.items():
      print(f"{chave}: {valor}")
  else:
    print("CEP não encontrado ou erro na consulta.")

if __name__ == "__main__":
  main()