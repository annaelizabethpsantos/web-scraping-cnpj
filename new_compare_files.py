import pandas as pd

def find_differences(cnpjs, found_cnpjs):
    setAll = set(cnpjs)
    setFound = set(found_cnpjs)
    not_found_cnpjs = setAll - setFound
    return list(not_found_cnpjs)

all = pd.read_excel('all_cnpjs.xlsx')

cnpjs_found = all.iloc[:, 0].tolist()

cnpjs_excel = 'levantamento.xlsx'
df = pd.read_excel(cnpjs_excel)
list_all_cnpjs = df.iloc[0:, 0].apply(lambda x: str(x).zfill(14)).apply(lambda x: f'{x[:2]}.{x[2:5]}.{x[5:8]}/{x[8:12]}-{x[12:]}').tolist()

not_found_cnpjs = find_differences(list_all_cnpjs, cnpjs_found)
df = pd.DataFrame({'CNPJ': not_found_cnpjs})
df.to_excel('cnpjs_nao_encontrados.xlsx', index=False)