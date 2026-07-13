#!/bin/bash
# scripts/download_reports_parallel.sh
# Uso: bash scripts/download_reports_parallel.sh BASE_URL START END CHUNK PAGINA1 [PAGINA2 ...]
# Exemplo: bash scripts/download_reports_parallel.sh http://3.224.52.81:5530 5000 10000 100 pagina2 pagina3 pagina4 pagina5

if [ "$#" -lt 5 ]; then
    echo "Uso: $0 BASE_URL START END CHUNK PAGINA1 [PAGINA2 ...]"
    echo "Exemplo: $0 http://3.224.52.81:5530 0 1000 100 pagina2 pagina3 pagina5"
    exit 1
fi

BASE_URL="$1"
START="$2"
END="$3"
CHUNK="$4"
shift 4
PAGINAS=("$@")   # todas as páginas restantes viram um array

for pagina in "${PAGINAS[@]}"; do
    OUTPUT_DIR="output/reports/${pagina}/"
    mkdir -p "$OUTPUT_DIR"

    echo "=== Página: ${pagina} | Range: ${START}-${END} | Chunk: ${CHUNK} ==="

    for ((start=START; start<END; start+=CHUNK)); do
        end=$((start + CHUNK))
        # Garante que a última faixa não ultrapasse o END
        if (( end > END )); then end=$END; fi

        echo "  Iniciando faixa ${start}-${end}..."
        bash scripts/download_reports_by_page_range.sh "$BASE_URL" "$pagina" "$start" "$end" "$OUTPUT_DIR" &
    done

    # Espera todas as faixas desta página antes de passar para a próxima
    wait
    echo "=== Página ${pagina} concluída ==="
done

echo "Todos os downloads finalizados."