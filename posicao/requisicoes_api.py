import requests
import os
import pandas as pd

from dotenv import load_dotenv
from processamento_excel import executa_ativos, resumir_ativos
from UUID import gerar_uuid
from utilidades import obter_data_mes_anterior

# Carregar variáveis de ambiente
load_dotenv()

# Constantes para URLs e autenticação
URL_API_TOKEN = os.getenv('API_URL_TOKEN')
CREDENCIAIS_BASIC_AUTH = os.getenv('BASIC_AUTH')
URL_API_POSICOES = os.getenv('API_POSITION_URL')
URL_API_DADOS_CADASTRAIS = os.getenv('API_URL_DADOS')


def obter_token_autenticacao():
    """Obtém o token de autenticação para requisições"""
    url = URL_API_TOKEN
    headers = {
        "Authorization": f"Basic {CREDENCIAIS_BASIC_AUTH}",
        "x-id-partner-request": gerar_uuid(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()

        # O token vem do cabeçalho, não do corpo da resposta
        token = response.headers.get('access_token')
        if not token:
            raise ValueError("Token não encontrado no cabeçalho da resposta.")
        return token

    except requests.exceptions.HTTPError as http_error:
        print(f"Erro HTTP: {http_error}")
    except Exception as e:
        print(f"Erro ao obter o token de autenticação: {e}")
    return None


def fazer_requisicao_posicao_cliente(codigo_cliente, data_requisicao, caminho_arquivo, token_autenticacao):
    """Faz requisição para obter os dados de posição do cliente e salva no Excel"""
    url = f"{URL_API_POSICOES}{codigo_cliente}"
    headers = {
        "x-id-partner-request": gerar_uuid(),
        "access_token": token_autenticacao
    }
    body = {"date": data_requisicao}

    try:
        resposta = requests.post(url, headers=headers, json=body)

        if resposta.status_code == 200:
            dados_posicao = resposta.json()
            numero_conta = dados_posicao.get('AccountNumber')
            print(f"Número da conta: {numero_conta}")

            # Salvar os dados no arquivo Excel
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as escritor:
                print("Processando ativos do cliente...")
                lista_ativos = executa_ativos(dados_posicao, escritor)

                # Resumir e salvar os dados dos ativos na aba 'resumo'
                print("Resumindo dados dos ativos...")
                resumir_ativos(lista_ativos, escritor)

        else:
            print(f"Erro na requisição. Código de status: {resposta.status_code}")
            print(f"Detalhes: {resposta.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição de posição do cliente: {e}")


# def fazer_requisicao_mes_anterior(codigo_cliente, data_atual, token_autenticacao):
#     """Faz requisição para obter os dados de posição do cliente do mês anterior"""
#     data_mes_anterior = obter_data_mes_anterior(data_atual)
#     url = f"{URL_API_POSICOES}{codigo_cliente}"
#     headers = {
#         "x-id-partner-request": gerar_uuid(),
#         "access_token": token_autenticacao
#     }
#     body = {"date": data_mes_anterior}
#
#     try:
#         resposta = requests.post(url, headers=headers, json=body)
#
#         if resposta.status_code == 200:
#             return resposta.json()
#
#         else:
#             print(f"Erro na requisição. Código de status: {resposta.status_code}")
#             print(f"Detalhes: {resposta.text}")
#     except Exception as e:
#         print(f"Erro ao fazer a requisição para o mês anterior: {e}")
#     return None


def obter_dados_cadastrais_cliente(codigo_cliente, token_autenticacao):
    """Faz requisição para obter os dados cadastrais do cliente"""
    url = URL_API_DADOS_CADASTRAIS.replace("{account_number}", codigo_cliente)
    headers = {
        "x-id-partner-request": gerar_uuid(),
        "access_token": token_autenticacao
    }

    try:
        resposta = requests.get(url, headers=headers)

        if resposta.status_code == 200:
            return resposta.json()
        elif resposta.status_code == 401:
            print("Código do cliente inválido. Tente novamente.")
            return None
    except Exception as e:
        print(f"Erro ao obter os dados cadastrais do cliente: {e}")
    return None
