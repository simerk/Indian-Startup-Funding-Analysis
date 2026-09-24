"""
data_cleaning.py
=================
Reproduces the cleaning pipeline used in the "Indian Startup Funding Analysis"
project, taking the raw export (Start-up_Funding1.csv) all the way through to
the analysis-ready file (Start-Up_funding_cleaned.csv).

The pipeline has three stages, matching the three intermediate files kept in
data/raw/ and data/processed/:

    Stage 1 – PARSE      Start-up_Funding1.csv   ->  (raw, one field per row)
    Stage 2 – SPLIT       ->  Start-up_Funding2.csv   (10 proper columns, still dirty)
    Stage 3 – DECLUTTER    ->  Start-Up_Funding.csv    (unwanted characters removed)
    Stage 4 – FINAL CLEAN  ->  Start-Up_funding_cleaned.csv (analysis-ready)

Run:
    python data_cleaning.py --input ../data/raw/Start-up_Funding1.csv --outdir ../data
"""

import argparse
import csv
import io
import re
import unicodedata

import pandas as pd

COLUMNS = [
    "Sr No", "Date dd/mm/yyyy", "Startup Name", "Industry Vertical",
    "Sub Vertical", "City  Location", "Investors Name", "Investment Type",
    "Amount in USD", "Remarks",
]


# ---------------------------------------------------------------------------
# Stage 1 & 2 — Parse the raw export and split it into proper columns
# ---------------------------------------------------------------------------
def parse_raw_export(path: str) -> pd.DataFrame:
    """
    Start-up_Funding1.csv was delivered as a broken export: every record was
    squashed into a single quoted field, terminated with a stray '||' and a
    UTF-8 byte-order mark on the first line, e.g.:

        "1,12/12/19,Ecozen,...,""60,00,000"",""||

    This function strips the '||' artifact and re-parses each line with
    Python's csv module (which correctly respects the doubled quotes), giving
    back the 10 real columns. This reproduces Start-up_Funding2.csv.
    """
    def clean_line(line: str) -> str:
        # Drop the trailing "||" delimiter artifact
        line = re.sub(r"\|\|\s*$", "", line).rstrip()
        # Each record is wrapped in one extra pair of quotes on top of the
        # normal CSV quoting (an export artifact) — strip that outer pair
        if line.startswith('"'):
            line = line[1:]
        if line.endswith('"'):
            line = line[:-1]
        # Undo the resulting double-escaped quotes (""x"" -> "x")
        line = line.replace('""', '"')
        return line

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        raw_lines = f.read().splitlines()

    cleaned_lines = [clean_line(line) for line in raw_lines]

    reader = csv.reader(io.StringIO("\n".join(cleaned_lines)))
    rows = list(reader)

    header, data_rows = rows[0], rows[1:]
    df = pd.DataFrame(data_rows, columns=header)
    return df


# ---------------------------------------------------------------------------
# Stage 3 — Remove unwanted characters (reproduces Start-Up_Funding.csv)
# ---------------------------------------------------------------------------
def fix_mojibake(text: str) -> str:
    """Best-effort fix for mis-decoded punctuation such as smart quotes that
    show up as escaped byte sequences (e.g. \\xe2\\x80\\x99)."""
    if not isinstance(text, str):
        return text
    text = text.replace("\\xe2\\x80\\x99", "'")
    text = text.replace("\\xc2\\xa0", " ")
    text = unicodedata.normalize("NFKC", text)
    return text


def standardize_spelling(text: str) -> str:
    if not isinstance(text, str):
        return text
    return re.sub(r"\b[eE][-\s]?[cC]ommerce\b", "E-commerce", text)


def standardize_date(text: str) -> str:
    """Normalize mixed separators (/, ., -) to '-' (keeps original order)."""
    if not isinstance(text, str):
        return text
    text = re.sub(r"[./]", "-", text.strip())
    return text


def remove_unwanted_characters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Declutters free-text columns:
      - fixes encoding artifacts (mojibake apostrophes etc.)
      - standardizes "Ecommerce" / "eCommerce" -> "E-commerce"
      - standardizes date separators to '-'
      - removes commas *inside* multi-value fields (Investors Name,
        Industry Vertical, Sub Vertical, City Location) so a single company
        with several investors reads as one clean string instead of a
        comma-separated fragment that collides with the CSV delimiter
      - trims stray whitespace
    """
    df = df.copy()

    text_cols = ["Startup Name", "Industry Vertical", "Sub Vertical",
                 "City  Location", "Investors Name"]
    for col in text_cols:
        df[col] = df[col].apply(fix_mojibake)

    for col in ["Industry Vertical", "Sub Vertical"]:
        df[col] = df[col].apply(standardize_spelling)

    multi_value_cols = ["Investors Name", "Industry Vertical",
                         "Sub Vertical", "City  Location"]
    for col in multi_value_cols:
        df[col] = df[col].apply(
            lambda x: re.sub(r"\s*,\s*", " ", x).strip() if isinstance(x, str) else x
        )

    df["Date dd/mm/yyyy"] = df["Date dd/mm/yyyy"].apply(standardize_date)

    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    return df


# ---------------------------------------------------------------------------
# Stage 4 — Final clean (matches the pandas steps used in the notebook)
# ---------------------------------------------------------------------------
def final_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reproduces the notebook steps shown in the project deck:
      1. Drop the 'Remarks' column (~86% empty, no analytical value)
      2. Drop rows with a null / 'Undisclosed' / 'Unknown' Amount in USD
      3. Strip thousands separators (',') and stray '+' from Amount in USD
      4. Cast Amount in USD to numeric
      5. Drop exact duplicate rows and fully empty rows
    """
    df = df.copy()

    if "Remarks" in df.columns:
        df = df.drop(columns=["Remarks"])

    df = df.dropna(subset=["Amount in USD"])
    df = df[~df["Amount in USD"].astype(str).str.strip().str.lower().isin(
        ["undisclosed", "unknown", ""]
    )]

    df["Amount in USD"] = (
        df["Amount in USD"].astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("+", "", regex=False)
    )
    df["Amount in USD"] = pd.to_numeric(df["Amount in USD"], errors="coerce")
    df = df.dropna(subset=["Amount in USD"])

    df = df.drop_duplicates()
    df = df.dropna(how="all")

    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------
def run_pipeline(input_path: str, outdir: str) -> None:
    print(f"Stage 1-2: parsing raw export from {input_path} ...")
    df_split = parse_raw_export(input_path)
    split_path = f"{outdir}/raw/Start-up_Funding2.reproduced.csv"
    df_split.to_csv(split_path, index=False)
    print(f"  -> {df_split.shape[0]} rows x {df_split.shape[1]} cols  saved to {split_path}")

    print("Stage 3: removing unwanted characters ...")
    df_declutter = remove_unwanted_characters(df_split)
    declutter_path = f"{outdir}/raw/Start-Up_Funding.reproduced.csv"
    df_declutter.to_csv(declutter_path, index=False)
    print(f"  -> saved to {declutter_path}")

    print("Stage 4: final clean (drop Remarks, fix Amount, dedupe) ...")
    df_final = final_clean(df_declutter)
    final_path = f"{outdir}/processed/Start-Up_funding_cleaned.reproduced.csv"
    df_final.to_csv(final_path, index=False)
    print(f"  -> {df_final.shape[0]} rows x {df_final.shape[1]} cols  saved to {final_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce the startup-funding cleaning pipeline.")
    parser.add_argument("--input", default="../data/raw/Start-up_Funding1.csv",
                         help="Path to the raw Start-up_Funding1.csv export")
    parser.add_argument("--outdir", default="../data",
                         help="Output directory (expects raw/ and processed/ subfolders)")
    args = parser.parse_args()
    run_pipeline(args.input, args.outdir)
