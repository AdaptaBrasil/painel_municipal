import csv
import os

CSV_PATH = "tabela_completa.csv"
PASTA_PDFS = "pagina5"
SAIDA = "county_id_nao_baixados_pagina5.txt"

nao_baixados = []

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    leitor = csv.DictReader(f)
    for linha in leitor:
        county_id = linha["county_id"].strip()
        geocode = linha["geocode"].strip()
        caminho_pdf = os.path.join(PASTA_PDFS, f"{geocode}.pdf")
        if not os.path.isfile(caminho_pdf):
            nao_baixados.append(county_id)

with open(SAIDA, "w", encoding="utf-8") as f:
    for county_id in nao_baixados:
        f.write(f"{county_id}\n")

print(f"Total não baixados: {len(nao_baixados)}")
print(f"Arquivo gerado: {SAIDA}")
