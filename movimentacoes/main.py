import requests
from .data_validation import obter_codigo_cliente_EM, obter_data_post_EM
from .api_requests import fazer_requisicao_movement
from .trate_data_csv import recebe_e_cria_movimentacao, formata_movimentacao, calcula_valor_liquido, destaca_negativos
from .executaServidor import webhook_completed_event

def movement_main(token, data_req, codigo_cliente, base_nome_arquivo):
    try:
        # Faz a requisição de movimento
        fazer_requisicao_movement(codigo_cliente, data_req[0], data_req[1], token)
    except Exception as e:
        print(f"Erro ao executar a requisição de movimento: {e}")
        return False

    print("Aguardando o término do processamento do webhook...")

    # Aguarda o evento do webhook ser completado ou o timeout
    if not webhook_completed_event.wait(timeout=90):
        print("Tempo de espera excedido. Cancelando a operação e retornando ao menu principal.")
        return False

    # Reseta o evento para o próximo loop
    webhook_completed_event.clear()

    # Processar o arquivo gerado após o webhook
    csv_filename = f'{codigo_cliente}.csv'
    try:
        excel_filename = recebe_e_cria_movimentacao(csv_filename, base_nome_arquivo)
        formata_movimentacao(excel_filename)
        calcula_valor_liquido(excel_filename)
        destaca_negativos(excel_filename)
        print("Processamento concluído com sucesso.")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return False

    return True
