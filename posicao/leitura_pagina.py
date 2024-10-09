from playwright.sync_api import sync_playwright
from utils import data_atual, data_mes_anterior

def submit_cnpj_and_calculate_rentabilidade(cnpj):
    with sync_playwright() as p:
        # Inicializando o navegador no modo headless (sem interface gráfica)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            acessar_dados_fundo(page, cnpj)

            mes_atual = data_atual()
            meses_anteriores = data_mes_anterior()

            # Capturar dados de cotas
            cotas_mes_atual = capturar_cotas_por_mes(page, mes_atual[1])
            cotas_mes_anterior = capturar_cotas_por_mes(page, mes_atual[0])

            # Capturar dados do mês anterior e anteriores a ele
            cotas_mes_antes_do_anterior = capturar_cotas_por_mes(page, meses_anteriores[1])
            cotas_mes_dois_antes = capturar_cotas_por_mes(page, meses_anteriores[0])

            # Determinar as últimas cotas de cada mês
            ultima_cota_mes_atual = ultima_cota(cotas_mes_atual)
            ultima_cota_mes_anterior = ultima_cota(cotas_mes_anterior)
            ultima_cota_mes_antes_do_anterior = ultima_cota(cotas_mes_antes_do_anterior)
            ultima_cota_mes_dois_antes = ultima_cota(cotas_mes_dois_antes)

            # # Exibir informações de cotas
            # print(f'Última cota do mês anterior: {ultima_cota_mes_anterior}')
            # print(f'Última cota do mês atual: {ultima_cota_mes_atual}')
            # print(f'Última cota do mês antes do anterior: {ultima_cota_mes_antes_do_anterior}')
            # print(f'Última cota do mês dois antes: {ultima_cota_mes_dois_antes}')

            # Calcular e exibir médias de rentabilidade
            rentabilidade_mes_atual = calcular_rentabilidade(ultima_cota_mes_anterior, ultima_cota_mes_atual)
            rentabilidade_mes_anterior = calcular_rentabilidade(ultima_cota_mes_dois_antes, ultima_cota_mes_antes_do_anterior)
            # print(f'Rentabilidade do mês atual: {rentabilidade_mes_atual:.2%}')
            # print(f'Rentabilidade do mês anterior: {rentabilidade_mes_anterior:.2%}')

        finally:
            browser.close()

        return rentabilidade_mes_atual, rentabilidade_mes_anterior


def ultima_cota(lista_de_cotas):
    """Retorna a última cota válida de uma lista."""
    cotas_validas = [cota for cota in lista_de_cotas if cota.strip()]  # Remove valores vazios
    return cotas_validas[-1] if cotas_validas else 'N/A'


def acessar_dados_fundo(page, cnpj):
    """Acessa diretamente a página de resultados do fundo usando o CNPJ fornecido."""
    # URL para acessar diretamente os resultados do fundo usando o CNPJ
    url = f"https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CConsolFdo/ResultBuscaParticFdo.aspx?CNPJNome={cnpj}&TpPartic=0&Adm=false&SemFrame="

    # Acessa a URL diretamente
    page.goto(url)

    # Espera até que o seletor do link que leva aos dados diários esteja disponível
    page.wait_for_selector('#ddlFundos__ctl0_Linkbutton2', timeout=10000)

    # Clica no link que leva aos dados diários
    page.click('#ddlFundos__ctl0_Linkbutton2')

    # Espera até que o link de dados diários esteja disponível e então clica nele
    page.wait_for_selector('#Hyperlink2', timeout=10000)
    page.click('#Hyperlink2')


def capturar_cotas_por_mes(page, mes):
    """Captura as cotas de um determinado mês na tabela de dados."""
    options = page.locator('#ddComptc option').all_inner_texts()

    if mes not in options:
        print(f"O mês {mes} não está disponível no dropdown.")
        return "O mês ainda não tem dados disponíveis."

    # Selecionar o mês desejado no dropdown
    page.select_option('#ddComptc', mes)

    # Aguardar a tabela e capturar as cotas
    page.wait_for_selector('#dgDocDiario', timeout=10000)
    linhas = page.locator('#dgDocDiario tbody tr').all()

    cotas = []
    for linha in linhas:
        celulas = linha.locator('td').all_inner_texts()  # Captura todas as células da linha
        if len(celulas) > 1:
            cotas.append(celulas[1])  # Captura o valor da cota na segunda célula

    return cotas


def calcular_rentabilidade(cota_inicial, cota_final):
    """Calcula a rentabilidade entre duas cotas e retorna como porcentagem formatada."""
    try:
        # Converte as cotas para float (substituindo vírgula por ponto)
        cota_inicial = float(cota_inicial.replace(',', '.'))
        cota_final = float(cota_final.replace(',', '.'))

        # Calcula a rentabilidade
        rentabilidade = (cota_final / cota_inicial - 1) * 100

        # Retorna a rentabilidade formatada como string com duas casas decimais e o símbolo de porcentagem
        return f"{rentabilidade:.2f}%"
    except ValueError:
        print(f"Erro ao converter cotas: cota_inicial = {cota_inicial}, cota_final = {cota_final}")
        return "N/A"

