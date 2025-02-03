import os

from requisicoes_api import fazer_requisicao_posicao_cliente, obter_token_autenticacao
from utilidades import limpar_tela, aplicar_formatacao_excel
from validacao_de_dados import obter_codigo_cliente, obter_data_post, data_atual
from base_clientes import ler_lista_clientes




def main():

    diretorio_destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios')
    os.makedirs(diretorio_destino, exist_ok=True)  # Cria o diretório "relatorios" se ele não existir


    while True:
        token = obter_token_autenticacao()
        try :
            print("Escolha a opção de processamento:")
            print("1 - Processar um único cliente")
            print("2 - Processar todos os clientes da lista")
            opcao = int(input("Digite a opção desejada: "))
            print("\n")

            if opcao == 1:
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

            elif opcao == 2:
                codigo_clientes, clientes = ler_lista_clientes()

                for codigo_clientes, nome_arquivo in zip(codigo_clientes, clientes):
                    date_req = data_atual()
                    cod_clie = codigo_clientes
                    base_nome_arquivo = nome_arquivo

                    # Adiciona um sufixo ao nome do arquivo se ele já existir
                    contador = 1
                    nome_arquivo = base_nome_arquivo
                    caminho_arquivo = os.path.join(diretorio_destino, f"{nome_arquivo}.xlsx")

                    while os.path.exists(caminho_arquivo):
                        nome_arquivo = f"{base_nome_arquivo} ({contador})"
                        caminho_arquivo = os.path.join(diretorio_destino, f"{nome_arquivo}.xlsx")
                        contador += 1

                    fazer_requisicao_posicao_cliente(cod_clie, date_req, caminho_arquivo, token)

                    # Aplicar a formatação monetária a todas as planilhas
                    aplicar_formatacao_excel(caminho_arquivo)
                    print("\n")

                # Pergunta ao usuário se deseja continuar
                resp = int(input("Deseja processar outro arquivo? (1 - Sim, 0 - Não): "))
                limpar_tela()
                if resp == 0:
                    # Usuário escolheu encerrar
                    break
        except Exception as e:
            print(f"Erro ao processar os dados: {e}")
            break
        resp = int(input("Deseja processar outro arquivo? (1 - Sim, 0 - Não): "))
        if resp == 0:
            break
        limpar_tela()
    print("Encerrando o programa.")

if __name__ == "__main__":
    main()

