import requests
import os
import pandas as pd

from dotenv import load_dotenv
from excel_processing import executa_ativos, resumir_ativos, Investimend_Fund
from UUID import gerador_uuid
from utils import data_mes_anterior


load_dotenv()

API_URL_TOKEN = os.getenv('API_URL_TOKEN')
BASIC_AUTH = os.getenv('BASIC_AUTH')

API_POSITION_URL = os.getenv('API_POSITION_URL')

API_URL_DADOS = os.getenv('API_URL_DADOS')


def required_token():
    url = API_URL_TOKEN
    headers = {
        "Authorization": f"Basic {BASIC_AUTH}",
        "x-id-partner-request": gerador_uuid(),
        "Content-Type": "application/x-www-form-urlencoded"  # Especifica o formato do conteúdo
    }
    body = {
        "grant_type": "client_credentials"
    }

    try:
        # Enviando o corpo como form-urlencoded
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()  # Verifica se houve algum erro na requisição

        # Extrai o token dos cabeçalhos da resposta
        token = response.headers.get('access_token')
        return token

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
    except Exception as e:
        print(f"Erro ao fazer a requisição: {e}")
    return None




def fazer_requisicao(cod_clie, date_req, file_path, token):
    url = f"{API_POSITION_URL}{cod_clie}"  # URL da API
    headers = {
        "x-id-partner-request": gerador_uuid(),
        "access_token": token
    }
    body = {
        "date": date_req
    }
    try:
        resposta = requests.post(url, headers=headers, json=body)

        if resposta.status_code == 200:
            dados = resposta.json()
            number_count = dados.get('AccountNumber')
            print(f"Número da conta: {number_count}")

            # Salva os dados no arquivo Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                print("Executando ativos...")
                list_ativos = executa_ativos(dados, writer)

                # Chamando a função para resumir os dados e salvar na aba 'resume_dados'
                print("Resumindo dados dos ativos...")
                resumir_ativos(list_ativos, writer)

        else:
            print(f"Falha na requisição. Status code: {resposta.status_code}")
            print("Detalhes:", resposta.text)
    except Exception as e:
        print("Erro ao fazer a requisição:", e)


def requisicao_dados_cadastrais(cod_clie, token):
    url = API_URL_DADOS.replace("{account_number}", cod_clie)
    headers = {
        "x-id-partner-request": "9d378c96-aa8b-4985-899e-863829ef4c7f",
        "access_token": token
    }
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            dados = resposta.json()
        if resposta.status_code == 401:
            print("Código do cliente inválido. Tente novamente.")
            return None
    except Exception as e:
        print("Erro ao fazer a requisição:", e)
    return dados

