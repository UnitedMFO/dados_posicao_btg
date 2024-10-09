import sys
import threading
import requests
from posicao.api_requests import required_token
from posicao.data_validation import obter_codigo_cliente, obter_data_post
from posicao.main import posicion_main
from movimentacoes.data_validation import obter_data_post_EM, obter_codigo_cliente_EM
from movimentacoes.main import movement_main
from movimentacoes.executaServidor import run_server  # Importa o servidor Flask
from posicao.utils import clear_screen

def main():
    # Iniciar o servidor Flask uma vez no início
    try:
        server_thread = threading.Thread(target=run_server)
        server_thread.start()
        print("Servidor Flask iniciado.")
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)

    while True:
        token = required_token()
        data_PM = obter_data_post()
        data_EM = obter_data_post_EM()
        cod_clie_PM, base_nome_arquivo_PM = obter_codigo_cliente(token, data_PM)
        cod_clie_EM, base_nome_arquivo_EM = obter_codigo_cliente_EM(token, data_PM, cod_clie_PM)

        # Executa posicion_main e movement_main
        posicion_main(token, data_PM, cod_clie_PM, base_nome_arquivo_PM)
        success = movement_main(token, data_EM, cod_clie_EM, base_nome_arquivo_EM)

        if success:
            print(f"Arquivo criado e salvo com sucesso!")
        else:
            print(f"Falha ao processar o arquivo.")

        # Pergunta ao usuário se deseja continuar
        resp = int(input("Deseja processar outro arquivo? (1 - Sim, 0 - Não): "))

        if resp == 0:
            # Usuário escolheu encerrar
            break
        clear_screen()

    # Encerrar o servidor Flask após o loop
    try:
        requests.post('http://127.0.0.1:5000/shutdown')
        server_thread.join()  # Aguarda que o servidor encerre corretamente
        print("Servidor Flask encerrado.")
    except Exception as e:
        print(f"Erro ao encerrar o servidor: {e}")

    print("Encerrando o programa.")
    sys.exit()

if __name__ == '__main__':
    main()