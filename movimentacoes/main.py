import threading
import requests
import time
import sys
from executaServidor import run_server, webhook_completed_event  # Importa o evento do servidor
from data_validation import obter_codigo_cliente, obter_data_post
from api_requests import required_token, fazer_requisicao_movement
from trate_data_csv import recebe_e_cria_movimentacao, formata_movimentacao, calcula_valor_liquido, destaca_negativos

def main():
    while True:
        token = required_token()
        data_req = obter_data_post()
        codigo_cliente, base_nome_arquivo = obter_codigo_cliente(token, data_req[0])

        try:
            server_thread = threading.Thread(target=run_server)
            server_thread.start()
            time.sleep(2)  # Certifica-se de que o servidor foi iniciado corretamente
        except Exception as e:
            print(f"Erro ao iniciar o servidor: {e}")
            continue

        try:
            fazer_requisicao_movement(codigo_cliente, data_req[0], data_req[1], token)
        except Exception as e:
            print(f"Erro ao executar a requisição de movimento: {e}")
            try:
                requests.post('http://127.0.0.1:5000/shutdown')
            except Exception as shutdown_error:
                print(f"Erro ao tentar encerrar o servidor após falha na requisição: {shutdown_error}")
            continue

        print("Aguardando o término do processamento do webhook...")

        # Espera indefinidamente até que o evento seja sinalizado
        webhook_completed_event.wait()  # Espera até que o webhook seja sinalizado

        # Reseta o evento para o próximo loop
        webhook_completed_event.clear()

        # Processar o arquivo gerado após o webhook
        csv_filename = f'{codigo_cliente}.csv'
        try:
            excel_filename = recebe_e_cria_movimentacao(csv_filename, base_nome_arquivo)
            formata_movimentacao(excel_filename)
            calcula_valor_liquido(excel_filename)
            destaca_negativos(excel_filename)

            # Encerra o servidor após o processamento bem-sucedido
            response = requests.post('http://127.0.0.1:5000/shutdown')
            if response.status_code == 200:
                print("Servidor encerrado com sucesso.")
            else:
                print(f"Falha ao encerrar o servidor: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            try:
                requests.post('http://127.0.0.1:5000/shutdown')
            except Exception as shutdown_error:
                print(f"Erro ao tentar encerrar o servidor: {shutdown_error}")

if __name__ == '__main__':
    main()
