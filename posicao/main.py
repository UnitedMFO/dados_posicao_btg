import os

from requisicoes_api import fazer_requisicao_posicao_cliente, obter_token_autenticacao
from utilidades import limpar_tela, aplicar_formatacao_excel
from validacao_de_dados import obter_codigo_cliente, obter_data_post




def main():

    diretorio_destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios')
    os.makedirs(diretorio_destino, exist_ok=True)  # Cria o diretório "relatorios" se ele não existir


    while True:
        token = obter_token_autenticacao()
        date_req = obter_data_post()
        cod_clie, base_nome_arquivo = obter_codigo_cliente(token,date_req)


        # Adiciona um sufixo ao nome do arquivo se ele já existir
        contador = 1
        nome_arquivo = base_nome_arquivo
        caminho_arquivo = os.path.join(diretorio_destino, f"{nome_arquivo}.xlsx")

        while os.path.exists(caminho_arquivo):
            nome_arquivo = f"{base_nome_arquivo} ({contador})"
            caminho_arquivo = os.path.join(diretorio_destino, f"{nome_arquivo}.xlsx")
            contador += 1


        # Supondo que você já tenha as funções para obter os dados e salvar no Excel
        fazer_requisicao_posicao_cliente(cod_clie, date_req, caminho_arquivo, token)

        # Aplicar a formatação monetária a todas as planilhas
        aplicar_formatacao_excel(caminho_arquivo)

        # Pergunta ao usuário se deseja continuar
        resp = int(input("Deseja processar outro arquivo? (1 - Sim, 0 - Não): "))
        limpar_tela()
        if resp == 0:
            # Usuário escolheu encerrar
            break



if __name__ == "__main__":
    main()

