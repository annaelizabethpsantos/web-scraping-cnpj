import pandas as pd

# Função para encontrar diferenças entre duas listas
def find_differences(cnpjs, found_cnpjs):
    setAll = set(cnpjs)
    setFound = set(found_cnpjs)
    not_found_cnpjs = setAll - setFound
    return list(not_found_cnpjs)

cnpjs_excel = 'levantamento.xlsx'
df = pd.read_excel(cnpjs_excel)
lista_cnpjs = df.iloc[0:, 0].apply(lambda x: str(x).zfill(14)).apply(lambda x: f'{x[:2]}.{x[2:5]}.{x[5:8]}/{x[8:12]}-{x[12:]}').tolist()


# Lista para armazenar diferenças
differences = []

# DataFrame para armazenar todos os arquivos encontrados_XXXX.xlsx
df_all_encontrados = pd.DataFrame(columns=['CNPJ', 'Arquivo'])

# 2. Para cada arquivo encontrados_XXXX.xlsx
for ano in range(2004, 2024):
    encontrado_file = f'encontrados_{ano}.xlsx'

    # Utiliza try-except para lidar com a ausência de alguns arquivos
    try:
        # Lê o arquivo e adiciona à lista
        df_encontrado = pd.read_excel(encontrado_file)

        # Adiciona à DataFrame geral
        df_all_encontrados = pd.concat([df_all_encontrados, df_encontrado])

    except FileNotFoundError:
        print(f'Arquivo não encontrado para o ano {ano}.')

not_found_cnpjs = find_differences(lista_cnpjs, df_all_encontrados['CNPJ'].tolist())
differences.extend(not_found_cnpjs)

# Cria um arquivo com todos os arquivos encontrados_XXXX.xlsx
df_all_encontrados.to_excel('all_found_cnpjs.xlsx', index=False)

# Cria um arquivo Excel com os CNPJs não encontrados
df_not_found = pd.DataFrame(columns=['CNPJ'])
df_not_found['CNPJ'] = differences
df_not_found.to_excel('not_found_cnpjs.xlsx', index=False)