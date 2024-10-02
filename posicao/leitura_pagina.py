from playwright.sync_api import sync_playwright
from .utils import data_atual

def submit_cnpj_and_access_link(cnpj):
    with sync_playwright() as p:
        # Inicializando o navegador no modo headless (sem interface gráfica)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            acessar_pagina_fundo(page, cnpj)

            mes_anterior, mes_atual = data_atual()

            # Capturar dados do mês anterior
            values_quotas_mes_anterior = capturar_dados_mes(page, mes_anterior)

            # Capturar dados do mês atual
            values_quotas_mes_atual = capturar_dados_mes(page, mes_atual)

            # Exibir a última cota
            ultima_cota_mes_anterior = ultima_quota(values_quotas_mes_anterior)
            ultima_cota_mes_atual = ultima_quota(values_quotas_mes_atual)
            print(f'Última cota do mês anterior: {ultima_cota_mes_anterior}')
            print(f'Cota Diaria do mês atual: {ultima_cota_mes_atual}')

            media = media_quotas(ultima_cota_mes_anterior, ultima_cota_mes_atual)
            print(f'Média de cota diária: {media:.2%}')

        finally:
            browser.close()

        return media


def ultima_quota(values_quotas):
    if(type(values_quotas) == str):
        return values_quotas
    quotas_filtradas = [quota for quota in values_quotas if quota.strip()]
    return quotas_filtradas[-1] if quotas_filtradas else 'N/A'


def acessar_pagina_fundo(page, cnpj):
    # Acessa a página inicial
    page.goto('https://cvmweb.cvm.gov.br/SWB//Sistemas/SCW/CPublica/CConsolFdo/FormBuscaParticFdo.aspx')

    # Inserir o CNPJ e selecionar o tipo de fundo
    page.fill('#txtCNPJNome', cnpj)
    page.select_option('#ddlTpFdo', '0')

    # Clicar em "Continuar" e navegar para os dados diários
    page.click('#btnContinuar')
    page.wait_for_selector('#ddlFundos__ctl0_Linkbutton2', timeout=10000)
    page.click('#ddlFundos__ctl0_Linkbutton2')

    page.wait_for_selector('#Hyperlink2', timeout=10000)
    page.click('#Hyperlink2')


def capturar_dados_mes(page, mes):
    """Função para selecionar um mês no dropdown e capturar os dados da tabela."""
    # Verificar se o mês desejado está disponível no dropdown
    options = page.locator('#ddComptc option').all_inner_texts()

    if mes not in options:
        print(f"O mês {mes} não está disponível no dropdown.")
        return "O mês ainda não tem dados disponíveis."

    # Selecionar o mês desejado no dropdown
    page.select_option('#ddComptc', mes)

    # Esperar até que a tabela esteja disponível
    page.wait_for_selector('#dgDocDiario', timeout=10000)

    # Capturar as linhas da tabela
    rows = page.locator('#dgDocDiario tbody tr').all()

    values_quotas = []
    for row in rows:
        cells = row.locator('td').all_inner_texts()
        if len(cells) > 1:
            values_quotas.append(cells[1])

    return values_quotas


def media_quotas(quota_anterior, quota_diaria):
    quota_anterior = float(quota_anterior.replace(',', '.'))
    quota_diaria = float(quota_diaria.replace(',', '.'))
    media = quota_diaria / quota_anterior - 1
    return media