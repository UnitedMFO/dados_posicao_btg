import pandas as pd
from quota_cvm import submit_cnpj_and_calculate_rentabilidade


def executa_ativos(dados, workbook, cod_clie=None, date_req=None, token=None):
    list_ativos = []

    # Função para tentar executar e capturar erros
    def executar_funcao(func, *args):
        try:
            result = func(*args)
            if result:  # Se o resultado não for None ou vazio, adiciona à lista
                list_ativos.append(result)
        except Exception as e:
            print(f"Erro ao executar {func.__name__}: {e}")

    # Chamando as funções de ativos individualmente, passando os parâmetros necessários
    executar_funcao(Investimend_Fund, dados, workbook, cod_clie, date_req, token)
    executar_funcao(FixedIncome, dados, workbook)
    executar_funcao(PensionInformations, dados, workbook)
    executar_funcao(Cash, dados, workbook)
    executar_funcao(FixedIncomeStructuredNote, dados, workbook)
    executar_funcao(StockPositions, dados, workbook)
    executar_funcao(CryptoCoin, dados, workbook)
    executar_funcao(Equities, dados, workbook)

    return list_ativos



def resumir_ativos(list_ativos, workbook):
    # Inicializando um dicionário para coletar os dados de resumo
    resumo = {
        'ticker': [],
        'netValue': [],
        'grossValue': []
    }
    for ativo in list_ativos:
        # Para cada ativo, assumimos que ele possui 'fundName', 'grossAssetValue', e 'netAssetValue'
        if 'ticker' in ativo and 'grossValue' in ativo and 'netValue' in ativo:
            resumo['ticker'].extend(ativo['ticker'])
            resumo['grossValue'].extend(ativo['grossValue'])
            resumo['netValue'].extend(ativo['netValue'])

    # Convertendo o dicionário de resumo para um DataFrame
    df_resumo = pd.DataFrame(resumo)

    # Escrevendo os dados na aba 'resume_dados' do Excel
    df_resumo.to_excel(workbook, sheet_name='Resumo', index=False)

    return df_resumo

def Investimend_Fund(dados, workbook, cod_clie, date_req, token):
    from requisicoes_api import fazer_requisicao_mes_anterior

    investment_fund = {
        'fundName': [],
        'ticker': [],
        'managerName': [],
        'fundLiquidity': [],
        'netValue': [],
        'grossValue': [],
        'virtualIOF': [],
        'incomeTax': [],
        'ir_iof': [],
        'rentabilidade_mes_atual': [],
        'rentabilidade_mes_anterior': [],
        'value_mes_anterior': []
    }

    try:
        # Obter a lista de fundos de investimentos do mês atual
        investimen_fund_list = dados.get('InvestmentFund', [])
        if not investimen_fund_list:
            raise ValueError("A lista 'InvestmentFund' está vazia ou não existe.")

        # Fazer a requisição para os dados do mês anterior fora do loop
        dados_mes_anterior = fazer_requisicao_mes_anterior(cod_clie, date_req, token)
        investimen_fund_list_mes_anterior = dados_mes_anterior.get('InvestmentFund', []) if dados_mes_anterior else []

        for i in range(len(investimen_fund_list)):
            investment_fund['fundName'].append(investimen_fund_list[i]['Fund']['FundName'])
            investment_fund['ticker'].append(investimen_fund_list[i]['Fund']['FundCNPJCode'])
            investment_fund['managerName'].append(investimen_fund_list[i]['Fund']['ManagerName'])
            investment_fund['fundLiquidity'].append(investimen_fund_list[i]['Fund']['FundLiquidity'])
            investment_fund['rentabilidade_mes_atual'].append(submit_cnpj_and_calculate_rentabilidade(investment_fund['ticker'][i])[0])
            investment_fund['rentabilidade_mes_anterior'].append(submit_cnpj_and_calculate_rentabilidade(investment_fund['ticker'][i])[1])

            total_gross_value = 0
            total_net_value = 0
            total_virtual_iof = 0
            total_income_tax = 0

            # Adicionar os valores para o mês atual
            for j in range(len(investimen_fund_list[i]['Acquisition'])):
                total_gross_value += float(investimen_fund_list[i]['Acquisition'][j]['GrossAssetValue'])
                total_net_value += float(investimen_fund_list[i]['Acquisition'][j]['NetAssetValue'])
                total_virtual_iof += float(investimen_fund_list[i]['Acquisition'][j]['VirtualIOF'])
                total_income_tax += float(investimen_fund_list[i]['Acquisition'][j]['IncomeTax'])

            investment_fund['grossValue'].append(float(f"{total_gross_value:.2f}"))
            investment_fund['netValue'].append(float(f"{total_net_value:.2f}"))
            investment_fund['incomeTax'].append(float(f"{total_income_tax:.2f}"))
            investment_fund['virtualIOF'].append(float(f"{total_virtual_iof:.2f}"))
            investment_fund['ir_iof'].append(float(f"{total_income_tax + total_virtual_iof:.2f}"))

            # Comparar e adicionar os valores do mês anterior
            total_gross_value_mes_anterior = 0
            for fund_anterior in investimen_fund_list_mes_anterior:
                if investimen_fund_list[i]['Fund']['FundCNPJCode'] == fund_anterior['Fund']['FundCNPJCode']:
                    for k in range(len(fund_anterior['Acquisition'])):
                        total_gross_value_mes_anterior += float(fund_anterior['Acquisition'][k]['GrossAssetValue'])
                    break  # Encontrou o fundo correspondente, pode sair do loop

            investment_fund['value_mes_anterior'].append(float(f"{total_gross_value_mes_anterior:.2f}"))

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        # Salvar os dados no arquivo Excel
        df = pd.DataFrame(investment_fund)
        df.to_excel(workbook, sheet_name='InvestmentFund', index=False)

    return investment_fund

def FixedIncome(dados, workbook):
    fixed_income = {
        'accountingGroupCode': [],
        'issuer': [],
        'ticker': [],
        'referenceIndexName': [],
        'indexYieldRate': [],
        'maturityDate': [],
        'netValue': [],
        'grossValue': [],
        'virtualIOF': [],
        'incomeTax': [],
        'ir_iof': []
    }
    try:
        fixed_income_list = dados.get('FixedIncome', [])

        if not fixed_income_list:
            raise ValueError("A lista 'FixedIncome' está vazia ou não existe.")

        for i in range(len(fixed_income_list)):
            fixed_income['accountingGroupCode'].append(fixed_income_list[i].get('AccountingGroupCode'))
            fixed_income['issuer'].append(fixed_income_list[i].get('Issuer'))
            fixed_income['ticker'].append(fixed_income_list[i].get('Ticker'))
            fixed_income['referenceIndexName'].append(fixed_income_list[i].get('ReferenceIndexName'))
            fixed_income['indexYieldRate'].append(fixed_income_list[i].get('IndexYieldRate'))
            fixed_income['maturityDate'].append(fixed_income_list[i].get('MaturityDate'))
            fixed_income['grossValue'].append(float(fixed_income_list[i]['GrossValue']))
            net_value = fixed_income_list[i].get('NetValue')
            virtual_iof = fixed_income_list[i].get('VirtualIOF')
            income_tax = fixed_income_list[i].get('IncomeTax')

            fixed_income['netValue'].append(float(net_value) if net_value is not None else 0.0)
            fixed_income['virtualIOF'].append(float(virtual_iof) if virtual_iof is not None else 0.0)
            fixed_income['incomeTax'].append(float(income_tax) if income_tax is not None else 0.0)
            fixed_income['ir_iof'].append(fixed_income['incomeTax'][i] + fixed_income['virtualIOF'][i])

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        df = pd.DataFrame(fixed_income)
        df.to_excel(workbook, sheet_name='FixedIncome', index=False)
    return fixed_income


def PensionInformations(dados,  workbook):
    pension_information = {
        'ticker': [],
        'netValue': [],
        'grossValue': [],
        'pensionCnpjCode': [],
    }
    try:
        pension_informations_list = dados.get('PensionInformations', [])

        if not pension_informations_list:
            raise ValueError("A lista 'PensionInformations' está vazia ou não existe.")

        for i in range(len(pension_informations_list)):
            for j in range(len(pension_informations_list[i]['Positions'])):
                pension_information['ticker'].append(pension_informations_list[i]['Positions'][j]['FundName'])
                pension_information['grossValue'].append(
                    float(pension_informations_list[i]['Positions'][j]['GrossAssetValue']))
                pension_information['netValue'].append(
                    float(pension_informations_list[i]['Positions'][j]['NetAssetValue']))
                pension_information['pensionCnpjCode'].append(
                    pension_informations_list[i]['Positions'][j]['PensionCnpjCode'])

    except (KeyError, IndexError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        df = pd.DataFrame(pension_information)
        df.to_excel(workbook, sheet_name='PensionInformations', index=False)
    return pension_information

def Cash(dados,  workbook):
    cash = {
        'ticker': [],
        'grossValue': [],
        'netValue': [],
    }
    try:
        cash_list = dados.get('Cash', [])

        if not cash_list:
            raise ValueError("A lista 'Cash' está vazia ou não existe.")

        soma = 0
        cash_invested = cash_list[0].get('CashInvested', [])
        for i in range(len(cash_invested)):
            soma += float(cash_invested[i].get('GrossValue'))

    except (IndexError, ValueError, KeyError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        cash['ticker'].append('cash')
        cash['grossValue'].append(soma)
        cash['netValue'].append(soma)
        df = pd.DataFrame(cash)
        df.to_excel(workbook, sheet_name='Cash', index=False)
    return cash


def FixedIncomeStructuredNote( dados, workbook):
    fixedIncomeStructuredNote = {
        'issuer': [],
        'maturityDate': [],
        'netValue': [],
        'grossValue': [],
        'accountingGroupCode': [],
        'iOFTax': [],
        'incomeTax': [],
        'ticker': [],
        'iof_tax': []
    }
    try:
        fixed_fund_list = dados.get('FixedIncomeStructuredNote', [])

        if not fixed_fund_list:
            raise ValueError("A lista 'FixedIncomeStructuredNote' está vazia ou não existe.")

        for i in range(len(fixed_fund_list)):
            fixedIncomeStructuredNote['issuer'].append(fixed_fund_list[i]['Issuer'])
            fixedIncomeStructuredNote['maturityDate'].append(fixed_fund_list[i]['MaturityDate'])
            fixedIncomeStructuredNote['grossValue'].append(float(fixed_fund_list[i]['GrossValue']))
            fixedIncomeStructuredNote['netValue'].append(float(fixed_fund_list[i]['NetValue']))
            fixedIncomeStructuredNote['accountingGroupCode'].append(fixed_fund_list[i]['AccountingGroupCode'])
            fixedIncomeStructuredNote['iOFTax'].append(float(fixed_fund_list[i]['IOFTax']))
            fixedIncomeStructuredNote['incomeTax'].append(float(fixed_fund_list[i]['IncomeTax']))
            fixedIncomeStructuredNote['ticker'].append(fixed_fund_list[i]['Ticker'])
            fixedIncomeStructuredNote['iof_tax'].append(
                float(fixed_fund_list[i]['IOFTax']) + float(fixed_fund_list[i]['IncomeTax']))

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        df = pd.DataFrame(fixedIncomeStructuredNote)
        df.to_excel(workbook, sheet_name='FixedIncomeStructuredNote', index=False)
    return fixedIncomeStructuredNote


def StockPositions( dados, workbook):
    stock_positions = {
        'ticker': [],
        'quantity': [],
        'grossValue': [],
        'netValue': [],
        'iSINCode': [],
        'isFII': [],
    }
    try:
        equities_list = dados.get('Equities', [])
        stock_position_list = equities_list[0].get('StockPositions', [])

        if not equities_list:
            raise ValueError("A lista 'StockPositions' está vazia ou não existe.")

        for i in range(len(stock_position_list)):
            stock_positions['ticker'].append(stock_position_list[i]['Ticker'])
            stock_positions['quantity'].append(stock_position_list[i]['Quantity'])
            stock_positions['grossValue'].append(float(stock_position_list[i]['GrossValue']))
            stock_positions['netValue'].append(float(stock_position_list[i]['GrossValue']))
            stock_positions['iSINCode'].append(stock_position_list[i]['ISINCode'])
            stock_positions['isFII'].append(stock_position_list[i]['IsFII'])

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")

    else:
        df = pd.DataFrame(stock_positions)
        df.to_excel(workbook, sheet_name='StockPositions', index=False)
    return stock_positions


def CryptoCoin( dados, workbook):
    cryptoCoin = {
        'ticker': [],
        'quantity': [],
        'grossValue': [],
        'netValue': []
    }
    try:
        crypt_list = dados.get('CryptoCoin', [])

        if not crypt_list:
            raise ValueError("A lista 'CryptoCoin' está vazia ou não existe.")

        for cripto in crypt_list:
            cryptoCoin['ticker'].append(cripto['Asset']['Name'])
            cryptoCoin['quantity'].append(cripto['Quantity'])
            cryptoCoin['grossValue'].append(float(cripto['GrossFinancial']))
            cryptoCoin['netValue'].append(float(cripto['GrossFinancial']))

        # Cria um DataFrame com os dados
        df_crypto = pd.DataFrame(cryptoCoin)

        # print("Dados a serem salvos:")
        # print(df_crypto.head())  # Exibe os primeiros registros para depuração

        # Salva o DataFrame em um arquivo Excel
        df_crypto.to_excel(workbook, sheet_name='CryptoCoin', index=False)

    except KeyError as e:
        print(f"Erro ao acessar a chave {str(e)}.")
    except ValueError as e:
        print(f"Erro de valor: {str(e)}")
    except TypeError as e:
        print(f"Erro de tipo: {str(e)}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {str(e)}")
    return cryptoCoin

def Equities( dados, workbook):
    equities = {
        'ticker': [],
        'quantity': [],
        'grossValue': [],
        'netValue': [],
    }
    try:
        equities_list = dados.get('Equities', [])
        stock_list = equities_list[0].get('StockLendingPositions', [])

        if not equities_list:
            raise ValueError("A lista 'Equities' está vazia ou não existe.")

        # Inicializa as listas para cada coluna
        equities['ticker'] = []
        equities['quantity'] = []
        equities['market_Value'] = []

        for stock in stock_list:
            equities['ticker'].append(stock['Ticker'])
            equities['quantity'].append(stock['Quantity'])
            equities['grossValue'].append(float(stock['MarketValue']))
            equities['netValue'].append(float(stock['MarketValue']))

        # Cria um DataFrame com os dados
        df_equities = pd.DataFrame(equities)

        # Salva o DataFrame em uma aba do arquivo Excel
        df_equities.to_excel(workbook, sheet_name='Equities', index=False)

    except KeyError as e:
        print(f"Erro ao acessar a chave {str(e)}.")
    except ValueError as e:
        print(f"Erro de valor: {str(e)}")
    except TypeError as e:
        print(f"Erro de tipo: {str(e)}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {str(e)}")
    return equities
