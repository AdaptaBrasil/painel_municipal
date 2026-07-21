# Usage: python3 check_not_downloaded.py --csv tabela_completa.csv --pdf-dir pagina4/
# Usage: python3 check_not_downloaded.py --pdf-dir pagina4/ --output faltantes.txt
# Usage: python3 check_not_downloaded.py --id-column county_id --filename-column geocode

import argparse
import csv
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check which county_ids from a CSV do not have a "
        "corresponding downloaded PDF."
    )
    parser.add_argument(
        "-c",
        "--csv",
        default="tabela_completa.csv",
        help="Path to the input CSV file (default: tabela_completa.csv).",
    )
    parser.add_argument(
        "-p",
        "--pdf-dir",
        default="pagina3",
        help="Directory containing the downloaded PDFs (default: pagina3).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output text file for the missing county_ids "
        "(default: county_id_not_downloaded_<pdf-dir>.txt).",
    )
    parser.add_argument(
        "--id-column",
        default="county_id",
        help="CSV column holding the identifier to report (default: county_id).",
    )
    parser.add_argument(
        "--filename-column",
        default="geocode",
        help="CSV column used to build the PDF filename (default: geocode).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    output = args.output
    if output is None:
        pdf_dir_name = os.path.basename(os.path.normpath(args.pdf_dir))
        output = f"county_id_not_downloaded_{pdf_dir_name}.txt"

    if not os.path.isfile(args.csv):
        sys.exit(f"CSV file not found: {args.csv}")
    if not os.path.isdir(args.pdf_dir):
        sys.exit(f"PDF directory not found: {args.pdf_dir}")

    not_downloaded = []

    with open(args.csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for column in (args.id_column, args.filename_column):
            if column not in (reader.fieldnames or []):
                sys.exit(f"Column '{column}' not found in {args.csv}")
        for row in reader:
            identifier = row[args.id_column].strip()
            filename = row[args.filename_column].strip()
            pdf_path = os.path.join(args.pdf_dir, f"{filename}.pdf")
            if not os.path.isfile(pdf_path):
                not_downloaded.append(identifier)

    with open(output, "w", encoding="utf-8") as f:
        for identifier in not_downloaded:
            f.write(f"{identifier}\n")

    print(f"Total not downloaded: {len(not_downloaded)}")
    print(f"Output file: {output}")


if __name__ == "__main__":
    main()
