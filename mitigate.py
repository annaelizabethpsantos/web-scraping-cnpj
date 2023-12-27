import pandas as pd

def find_differences(list1, list2):
    setAll = set(list1)
    setFound = set(list2)
    difference = setAll - setFound
    return list(difference)

all1 = pd.read_excel('all_cnpjs.xlsx')
cnpjs_found1 = all1.iloc[:, 0].tolist()

all2 = pd.read_excel('all_found_cnpjs.xlsx')
cnpjs_found2 = all2.iloc[:, 0].tolist()

list_diff = find_differences(cnpjs_found1, cnpjs_found2)

print(f"Differences: {list_diff}")
print(len(list_diff))
print(list_diff)