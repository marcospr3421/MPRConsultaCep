import requests

def consultar_cep(cep, token):
  """
  Consulta informações de um CEP usando a API dos Correios.

  Args:
    cep: O CEP a ser consultado (string, apenas números).
    token: O token de acesso da API dos Correios.

  Returns:
    Um dicionário com as informações do CEP, ou None em caso de erro.
  """

  url = f"https://api.correios.com.br/cep/v2/enderecos/{cep}"
  headers = {
      "Authorization": f"Bearer {token}"
  }

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f"Erro ao consultar CEP: {e}")
    return None

def main():
  """
  Função principal que solicita o CEP e o token ao usuário e exibe as informações.
  """

  cep = input("Digite o CEP (apenas números): ")
  token = "eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzYzNjExODIsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3MzY0NDc1ODIsImp0aSI6IjhmNjVlNjEyLWIwYmEtNGI3Zi1iMWJlLTAxMTVlMDI0N2IyNCIsImFtYmllbnRlIjoiUFJPRFVDQU8iLCJwZmwiOiJQSiIsImlwIjoiNDUuMjI3LjYxLjI0NiwgMTkyLjE2OC4xLjEzMCIsImNhdCI6IlBsMCIsImNvbnRyYXRvIjp7Im51bWVybyI6Ijk5MTIzNzM3MzQiLCJkciI6NzIsImFwaXMiOlt7ImFwaSI6Mjd9LHsiYXBpIjozNH0seyJhcGkiOjM1fSx7ImFwaSI6NDF9LHsiYXBpIjo3Nn0seyJhcGkiOjc4fSx7ImFwaSI6ODd9LHsiYXBpIjo1NjZ9LHsiYXBpIjo1ODZ9LHsiYXBpIjo1ODd9LHsiYXBpIjo2MjF9LHsiYXBpIjo2MjN9XX0sImlkIjoiYXpjb21lcmNpbyIsImNucGoiOiIyMDM4NDg0OTAwMDExMyJ9.l8zENOSVUqIBfPquRPQjBRhPLilnHCDklJtGHxU2e1obHpSsZ9au_AMTdv7sWksdcOE_IaCTmfm0pmjPK01G9atRrf7GBq1Eh1Z2d-YmPkyFnEYbV1zF3pLgACYYmCdFxuvXR0uhCteWIeTz5Wn1-DIVT2CkpgKxGr2uq3QzBnuGUtmQZeXW0wdHZ6ebmRu9GeagG4lm-i3fTvweyBQnWGFCCZj9wlwKNTmfwyv-zApCenWGqVUZDXaPIgqc6CP6lb7oLCuwXSKYrRzKI4qYg9cBYkTCc60oWfJvRR0ci4OB-LNZu-vpdjGGf7cs5hauVUQ0eeJGFwV3kqgGTQeHWw'"

  dados_cep = consultar_cep(cep, token)

  if dados_cep:
    print("\nInformações do CEP:")
    for chave, valor in dados_cep.items():
      print(f"{chave}: {valor}")
  else:
    print("CEP não encontrado ou erro na consulta.")

if __name__ == "__main__":
  main()