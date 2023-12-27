import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
import fitz
import requests
from requests.exceptions import ChunkedEncodingError, RequestException

# Diretório de saída para os PDFs
output_directory = 'pdfs'
directory_cnpjs = 'cnpj'
# URL base
url_base = 'https://auniao.pb.gov.br/servicos/doe'
# Carregar a lista de CNPJs
cnpjs_excel = 'levantamento.xlsx'
df = pd.read_excel(cnpjs_excel)
lista_cnpjs = df.iloc[0:, 0].apply(lambda x: str(x).zfill(14)).apply(lambda x: f'{x[:2]}.{x[2:5]}.{x[5:8]}/{x[8:12]}-{x[12:]}').tolist()
found_cnpj =[]
found_cnpj_df = pd.DataFrame(columns=['CNPJ', 'Arquivo'])
found_cnpjs_file = 'found_cnpjs.txt'
not_found_cnpjs_file = 'not_found_cnpjs.txt'
url_inexistente = 'url_not_exists.txt'
line = []
def make_request(url, max_retries=7):
    for _ in range(max_retries):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()  # Lança uma exceção para códigos de status HTTP de erro
            return response
        except (ChunkedEncodingError, RequestException) as e:
            print(f"Erro na requisição: {e}")
            print("Tentando novamente...")
    return None
def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False
def baixar_pdfs_para_lista(url_base, output_directory):
    anos = ['/2022']
    meses = ['/janeiro', '/fevereiro', '/marco', '/abril', '/maio', '/junho', '/julho', '/agosto', '/setembro', '/outubro', '/novembro', '/dezembro']
    global found_cnpj_df
    for ano in reversed(anos):
        for mes in meses:
            url_temporaria = url_base + ano + mes
            for iterator in [0, 20]:
                url = f'{url_temporaria}?b_start:int={iterator}'
                print(f'Processando URL: {url}')
                if not url_exists(url):
                    with open(url_inexistente, 'a') as txt_file:
                        txt_file.write(f"URL não existe: {url}\n")
                    print(f'URL não existe: {url}')
                else:
                    processar_pagina(url, output_directory, directory_cnpjs)

def get_html_content(pdf_url, output_directory):
    # Baixar o PDF
    pdf_response = make_request(pdf_url)

    # Verificar se o download foi bem-sucedido
    if pdf_response.status_code == 200:
        pdf_filename = pdf_url.split("/")[-1]
        pdf_path = os.path.join(output_directory, pdf_filename)

        # Salvar o PDF no diretório de saída
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)

        # Converter o PDF para HTML
        html_content = convert_pdf_to_html(pdf_path)

        # Excluir o PDF após o download e a conversão
        delete_pdf(pdf_path)

        return html_content

    else:
        print(f"Falha ao baixar {pdf_url}")
        return None

def convert_pdf_to_html(pdf_path):
    doc = fitz.open(pdf_path)
    html_data = ""

    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("html")
        html_data += f"<div id='page-{page_num + 1}'>{text}</div>"

    doc.close()

    return html_data

def download_pdf(pdf_url, output_directory):
    # Baixar o PDF
    pdf_response = make_request(pdf_url)

    # Verificar se o download foi bem-sucedido
    if pdf_response.status_code == 200:
        pdf_filename = pdf_url.split("/")[-1]
        pdf_path = os.path.join(output_directory, pdf_filename)

        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)

    else:
        print(f"Falha ao baixar {pdf_url}")

def processar_pagina(url, output_directory, directory_cnpjs):
    # Fazer uma solicitação GET para obter o conteúdo da página
    response = make_request(url)
    global found_cnpj_df
    # Verificar se a solicitação foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Criar um objeto BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todos os links na página
        links = soup.find_all('a')

        # Iterar sobre os links e baixar os PDFs
        for link in links:
            href = link.get('href')
            if href and href.endswith('.pdf/view'):
                responsePDF = make_request(href)
                if responsePDF.status_code == 200:
                    # Criar um objeto BeautifulSoup para analisar o HTML
                    soupPDF = BeautifulSoup(responsePDF.text, 'html.parser')

                    # Encontrar todos os links na página
                    linksPDF = soupPDF.find_all('a')
                    for linkPDF in linksPDF:
                        hrefPDF = linkPDF.get('href')
                        if hrefPDF and hrefPDF.endswith('.pdf'):
                            html_content = get_html_content(hrefPDF, output_directory)
                            found_cnpj_in_pdf = False
                            for cnpj in lista_cnpjs:
                                if cnpj in html_content:
                                    found_cnpj_in_pdf = True
                                    found_cnpj_df.loc[len(found_cnpj_df)] = {'CNPJ': cnpj, 'Arquivo': hrefPDF.split("/")[-1]}
                                    print("Encontrado CNPJ " + cnpj + " no arquivo " + hrefPDF.split("/")[-1])
                                    with open(found_cnpjs_file, 'a') as txt_file:
                                        txt_file.write(f"{cnpj} ,{hrefPDF.split('/')[-1]}\n")
                                    # Se sim, fazer o download do PDF
                                    download_pdf(hrefPDF, directory_cnpjs)
                            if not found_cnpj_in_pdf:
                                # Se nenhum CNPJ da lista foi encontrado, imprimir uma mensagem
                                with open(not_found_cnpjs_file, 'a') as txt_file:
                                    txt_file.write(f"O PDF {href} não contém nenhum CNPJ da lista.\n")
                                print(f"O PDF {href} não contém nenhum CNPJ da lista.")

def delete_pdf(pdf_path):
    # Excluir o arquivo PDF
    os.remove(pdf_path)
def find_differences (cnpjs, found_cnpjs):
    set1 = set(cnpjs)
    set2 = set(found_cnpjs)
    not_found_cnpjs = set1 - set2
    return list(not_found_cnpjs)
# Executar o download dos PDFs
baixar_pdfs_para_lista(url_base, output_directory)
# Adicionando o CNPJ ao arquivo .txt
with open(not_found_cnpjs_file, 'a') as txt_file:
    txt_file.write(str("".join(find_differences(lista_cnpjs, found_cnpj)) + "\n"))
found_cnpj_df.to_excel('encontrados_2022.xlsx', index=False, engine='openpyxl')
print("Lista de CNPJs não encontrados: " + str(find_differences(lista_cnpjs, found_cnpj)))
