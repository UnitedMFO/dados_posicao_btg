from utils import validar_data
from api_requests import requisicao_dados_cadastrais
from datetime import date,timedelta

def obter_data_post():

    date_req = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')

    # Solicita ao usuário se deseja alterar a data padrão
    if int(input(f"A data padrão para a POSIÇÃO MENSAL é ({date_req}) - Deseja alterar? (1 - Sim, 0 - Não): ")) == 1:
        while True:
            date_req_temp = input("Digite a data desejada (AAAA-MM-DD): ")
            if validar_data(date_req_temp):
                return date_req_temp
            print("Formato de data inválido, tente novamente.")

    return date_req




def obter_codigo_cliente(token,data):
    while True:
        codigo_cliente = input("Digite o código do cliente: ")

        # Verifica se o código tem 9 caracteres e é composto apenas de números
        if len(codigo_cliente) == 9 and codigo_cliente.isdigit():
            dados = requisicao_dados_cadastrais(codigo_cliente, token)

            # Se os dados forem válidos, retorna; caso contrário, informa o erro e repete o loop
            if dados is not None:
                nome_completo = dados.get('holder')['name'].split()
                data_atual = data.split('-')
                iniciais = ''
                for nome in nome_completo:
                    iniciais += nome[0]

                iniciais = iniciais + "_PM_" + data_atual[1] + "_" + data_atual[0]

                return codigo_cliente,iniciais
            else:
                print("Código do cliente inválido. Tente novamente.")
        else:
            print("O Código do cliente deve ter 9 números. Tente novamente.")



