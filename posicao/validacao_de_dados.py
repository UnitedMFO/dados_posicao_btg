from utilidades import validar_formato_data
from requisicoes_api import obter_dados_cadastrais_cliente
from datetime import date, timedelta


def obter_data_post():
    """Obtém a data de requisição para a posição mensal. Pergunta ao usuário se deseja alterar a data padrão."""
    data_padrao = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')

    # Pergunta ao usuário se deseja alterar a data padrão
    alterar_data = int(
        input(f"A data padrão para a POSIÇÃO MENSAL é ({data_padrao}) - Deseja alterar? (1 - Sim, 0 - Não): "))

    if alterar_data == 1:
        while True:
            data_informada = input("Digite a data desejada (AAAA-MM-DD): ")
            if validar_formato_data(data_informada):
                return data_informada
            print("Formato de data inválido, tente novamente.")

    return data_padrao

def data_atual():
    """Retorna a data atual no formato AAAA-MM-DD."""
    data_padrao = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
    return data_padrao

def obter_codigo_cliente(token, data_requisicao):
    """Obtém o código do cliente e gera um identificador único baseado no nome do cliente e na data."""
    while True:
        codigo_cliente = input("Digite o código do cliente: ")

        # Verifica se o código do cliente é válido (9 dígitos)
        if len(codigo_cliente) == 9 and codigo_cliente.isdigit():
            dados_cliente = obter_dados_cadastrais_cliente(codigo_cliente, token)

            # Se os dados do cliente forem válidos, gera as iniciais e retorna
            if dados_cliente is not None:
                nome_completo = dados_cliente.get('holder', {}).get('name', '').split()
                data_formatada = data_requisicao.split('-')

                # Gera as iniciais a partir do nome completo
                iniciais_cliente = ''.join([nome[0] for nome in nome_completo])

                # Monta o identificador com iniciais, mês e ano
                identificador_cliente = f"{iniciais_cliente}_PM_{data_formatada[1]}_{data_formatada[0]}"

                return codigo_cliente, identificador_cliente
            else:
                print("Código do cliente inválido ou não encontrado. Tente novamente.")
        else:
            print("O código do cliente deve ter 9 dígitos numéricos. Tente novamente.")

