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


def processar_ativos(dados, tipo_ativo, workbook, sheet_name, campos, campos_opcionais=None):
    ativos = {campo: [] for campo in campos}

    # Adiciona campos opcionais (como iOF ou incomeTax)
    if campos_opcionais:
        for campo in campos_opcionais:
            ativos[campo] = []

    try:
        ativo_list = dados.get(tipo_ativo, [])
        if not ativo_list:
            raise ValueError(f"A lista '{tipo_ativo}' está vazia ou não existe.")

        for ativo in ativo_list:
            for campo in campos:
                ativos[campo].append(ativo.get(campo, 'N/A'))

            # Processa campos opcionais
            if campos_opcionais:
                for campo in campos_opcionais:
                    ativos[campo].append(float(ativo.get(campo, 0)))

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro ao processar {tipo_ativo}: {str(e)}")
    else:
        # Salva no Excel
        df = pd.DataFrame(ativos)
        df.to_excel(workbook, sheet_name=sheet_name, index=False)

    return ativos


def process_acquisition(acquisition_list):
    total_gross_value = 0
    total_net_value = 0
    total_virtual_iof = 0
    total_income_tax = 0

    for acquisition in acquisition_list:
        total_gross_value += float(acquisition['GrossAssetValue'])
        total_net_value += float(acquisition['NetAssetValue'])
        total_virtual_iof += float(acquisition['VirtualIOF'])
        total_income_tax += float(acquisition['IncomeTax'])

    return total_gross_value, total_net_value, total_virtual_iof, total_income_tax


def Investimend_Fund(dados, workbook, cod_clie, date_req, token):
    from requisicoes_api import requisicao_mes_anterior

    investment_fund = {
        'fundName': [], 'ticker': [], 'managerName': [], 'fundLiquidity': [],
        'netValue': [], 'grossValue': [], 'virtualIOF': [], 'incomeTax': [],
        'ir_iof': [], 'rentabilidade_mes_atual': [], 'rentabilidade_mes_anterior': [],
        'value_mes_anterior': []
    }

    try:
        investimen_fund_list = dados.get('InvestmentFund', [])
        if not investimen_fund_list:
            raise ValueError("A lista 'InvestmentFund' está vazia ou não existe.")

        # Requisição para mês anterior
        dados_mes_anterior = requisicao_mes_anterior(cod_clie, date_req, token)
        investimen_fund_list_mes_anterior = dados_mes_anterior.get('InvestmentFund', []) if dados_mes_anterior else []

        for fund in investimen_fund_list:
            investment_fund['fundName'].append(fund['Fund']['FundName'])
            investment_fund['ticker'].append(fund['Fund']['FundCNPJCode'])
            investment_fund['managerName'].append(fund['Fund']['ManagerName'])
            investment_fund['fundLiquidity'].append(fund['Fund']['FundLiquidity'])
            investment_fund['rentabilidade_mes_atual'].append(submit_cnpj_and_calculate_rentabilidade(fund['Fund']['FundCNPJCode'])[0])
            investment_fund['rentabilidade_mes_anterior'].append(submit_cnpj_and_calculate_rentabilidade(fund['Fund']['FundCNPJCode'])[1])

            total_gross_value, total_net_value, total_virtual_iof, total_income_tax = process_acquisition(fund['Acquisition'])

            investment_fund['grossValue'].append(total_gross_value)
            investment_fund['netValue'].append(total_net_value)
            investment_fund['incomeTax'].append(total_income_tax)
            investment_fund['virtualIOF'].append(total_virtual_iof)
            investment_fund['ir_iof'].append(total_income_tax + total_virtual_iof)

            # Processar mês anterior
            total_gross_value_mes_anterior = 0
            for fund_anterior in investimen_fund_list_mes_anterior:
                if fund['Fund']['FundCNPJCode'] == fund_anterior['Fund']['FundCNPJCode']:
                    total_gross_value_mes_anterior, *_ = process_acquisition(fund_anterior['Acquisition'])
                    break
            investment_fund['value_mes_anterior'].append(total_gross_value_mes_anterior)

    except (KeyError, ValueError, TypeError) as e:
        print(f"Erro: {str(e)}")
    else:
        pd.DataFrame(investment_fund).to_excel(workbook, sheet_name='InvestmentFund', index=False)

    return investment_fund


def FixedIncome(dados, workbook):
    campos = ['accountingGroupCode', 'issuer', 'ticker', 'referenceIndexName', 'indexYieldRate', 'maturityDate']
    campos_opcionais = ['grossValue', 'netValue', 'virtualIOF', 'incomeTax', 'ir_iof']
    return processar_ativos(dados, 'FixedIncome', workbook, 'FixedIncome', campos, campos_opcionais)

def PensionInformations(dados, workbook):
    campos = ['ticker', 'netValue', 'grossValue', 'pensionCnpjCode']
    return processar_ativos(dados, 'PensionInformations', workbook, 'PensionInformations', campos)

def FixedIncomeStructuredNote(dados, workbook):
    campos = ['issuer', 'maturityDate', 'netValue', 'grossValue', 'accountingGroupCode']
    campos_opcionais = ['iOFTax', 'incomeTax', 'iof_tax']
    return processar_ativos(dados, 'FixedIncomeStructuredNote', workbook, 'FixedIncomeStructuredNote', campos, campos_opcionais)

def StockPositions(dados, workbook):
    campos = ['ticker', 'quantity', 'grossValue', 'netValue', 'iSINCode', 'isFII']
    return processar_ativos(dados, 'StockPositions', workbook, 'StockPositions', campos)


def CryptoCoin(dados, workbook):
    campos = ['ticker', 'quantity', 'grossValue', 'netValue']
    return processar_ativos(dados, 'CryptoCoin', workbook, 'CryptoCoin', campos)


def Equities(dados, workbook):
    campos = ['ticker', 'quantity', 'grossValue', 'netValue']
    return processar_ativos(dados, 'Equities', workbook, 'Equities', campos)


def Cash(dados, workbook):
    cash_data = {
        'ticker': ['cash'],
        'grossValue': [],
        'netValue': []
    }
    try:
        cash_list = dados.get('Cash', [])
        if not cash_list:
            raise ValueError("A lista 'Cash' está vazia ou não existe.")

        soma = sum(float(cash.get('GrossValue', 0)) for cash in cash_list[0].get('CashInvested', []))
        cash_data['grossValue'].append(soma)
        cash_data['netValue'].append(soma)

    except (IndexError, ValueError, KeyError, TypeError) as e:
        print(f"Erro ao processar Cash: {str(e)}")
    else:
        pd.DataFrame(cash_data).to_excel(workbook, sheet_name='Cash', index=False)

    return cash_data






