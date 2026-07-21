#!/usr/bin/env python3
"""
Verifica a porcentagem de geocodes já baixados.

Cruza os geocodes esperados (coluna 'geocode' de tabela_completa.csv) com os
PDFs presentes na pasta informada (ex: pagina4/), cujos nomes seguem o padrão
<geocode>.pdf. Ao final, relata quantos foram baixados, quantos faltam e
quantos arquivos existem na pasta mas não constam na tabela (extras).

Uso:
    python3 check_download_percentage.py pagina4/ tabela_completa.csv
"""

import argparse
import csv
import sys
from pathlib import Path


def carregar_geocodes(caminho_csv: Path) -> set:
    """Lê o CSV e devolve o conjunto de geocodes esperados (sem duplicatas/vazios)."""
    geocodes = set()
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        # Aborta cedo se a coluna obrigatória não existir, evitando KeyError adiante.
        if leitor.fieldnames is None or "geocode" not in leitor.fieldnames:
            sys.exit(f"Erro: coluna 'geocode' não encontrada em {caminho_csv}")
        for linha in leitor:
            geocode = linha["geocode"].strip()
            if geocode:  # ignora células em branco
                geocodes.add(geocode)
    return geocodes


def listar_baixados(pasta: Path) -> set:
    """Devolve o conjunto de geocodes já baixados (o nome de cada PDF sem a extensão)."""
    return {arquivo.stem for arquivo in pasta.glob("*.pdf")}


def main():
    parser = argparse.ArgumentParser(
        description="Verifica quantos %% dos geocodes já foram baixados."
    )
    parser.add_argument("pasta", type=Path, help="Pasta com os PDFs baixados (ex: pagina4/)")
    parser.add_argument("csv", type=Path, help="Arquivo CSV com a tabela completa (ex: tabela_completa.csv)")
    args = parser.parse_args()

    # Valida os caminhos antes de processar, com mensagens claras em vez de stack trace.
    if not args.pasta.is_dir():
        sys.exit(f"Erro: pasta não encontrada: {args.pasta}")
    if not args.csv.is_file():
        sys.exit(f"Erro: arquivo não encontrado: {args.csv}")

    esperados = carregar_geocodes(args.csv)
    baixados_na_pasta = listar_baixados(args.pasta)

    # Operações de conjunto: interseção = baixados; diferenças = faltantes e extras.
    baixados = esperados & baixados_na_pasta        # esperados que já estão na pasta
    faltantes = esperados - baixados_na_pasta       # esperados que ainda faltam baixar
    extras = baixados_na_pasta - esperados          # PDFs na pasta fora da tabela

    # Percentuais calculados sobre o total esperado (guarda contra divisão por zero).
    total = len(esperados)
    pct_baixado = 100 * len(baixados) / total if total else 0.0
    pct_faltante = 100 * len(faltantes) / total if total else 0.0

    print("=" * 50)
    print(f"Pasta analisada:      {args.pasta}")
    print(f"Tabela de referência: {args.csv}")
    print("=" * 50)
    print(f"Total a ser baixado:  {total}")
    print(f"Arquivos baixados:    {len(baixados)} ({pct_baixado:.2f}%)")
    print(f"Arquivos faltantes:   {len(faltantes)} ({pct_faltante:.2f}%)")
    if extras:
        print(f"Arquivos na pasta fora da tabela: {len(extras)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
