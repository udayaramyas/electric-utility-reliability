"""Prepare the official EIA-861 reliability workbook for Power BI."""
from pathlib import Path
from urllib.request import urlopen
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
EXTRACT = RAW / "extract"
SOURCE_ZIP = RAW / "eia861_2025.zip"
SOURCE_URL = "https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip"
RELIABILITY_XLSX = EXTRACT / "Reliability_2025.xlsx"
DATA = ROOT / "data"
RESULTS = ROOT / "results"


def get_source_workbook():
    if not RELIABILITY_XLSX.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        if not SOURCE_ZIP.exists():
            print(f"Downloading {SOURCE_URL}")
            with urlopen(SOURCE_URL, timeout=90) as response:
                SOURCE_ZIP.write_bytes(response.read())
        EXTRACT.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(SOURCE_ZIP) as archive:
            member = next(name for name in archive.namelist() if name.endswith("Reliability_2025.xlsx"))
            (EXTRACT / "Reliability_2025.xlsx").write_bytes(archive.read(member))
    return RELIABILITY_XLSX


def numeric(series):
    return pd.to_numeric(series.replace({".": None, "": None}), errors="coerce")


def main():
    source = get_source_workbook()
    DATA.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    state_raw = pd.read_excel(source, sheet_name="State Totals", header=2)
    state = state_raw[state_raw.iloc[:, 0] == 2025].iloc[:, [0, 1, 12, 13, 14, 15, 16, 17, 18]].copy()
    state.columns = [
        "year", "state", "customer_count_any_standard", "saidi_with_med_minutes",
        "saifi_with_med_interruptions", "caidi_with_med_minutes",
        "saidi_without_med_minutes", "saifi_without_med_interruptions", "caidi_without_med_minutes",
    ]
    for col in state.columns[2:]:
        state[col] = numeric(state[col])
    state = state.dropna(subset=["state"]).sort_values("state")
    state.to_csv(DATA / "state_totals.csv", index=False)

    utility_raw = pd.read_excel(source, sheet_name="Reliability_States", header=2)
    utility = utility_raw[utility_raw.iloc[:, 0] == 2025].iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16]].copy()
    utility.columns = [
        "year", "utility_id", "utility_name", "state", "ownership",
        "ieee_saidi_with_med_minutes", "ieee_saifi_with_med_interruptions", "ieee_caidi_with_med_minutes",
        "ieee_saidi_without_med_minutes", "ieee_saifi_without_med_interruptions", "ieee_caidi_without_med_minutes",
        "customer_count", "highest_distribution_voltage_kv", "outages_recorded_automatically",
    ]
    for col in utility.columns[5:13]:
        utility[col] = numeric(utility[col])
    utility = utility.dropna(subset=["utility_id", "utility_name", "state"]).sort_values(["state", "utility_name"])
    utility.to_csv(DATA / "utility_reliability.csv", index=False)

    saidi = state.dropna(subset=["saidi_with_med_minutes"])
    no_med = state.dropna(subset=["saidi_without_med_minutes"])
    report = [
        "EIA Form 861 Reliability | 2025 final data",
        f"Source archive: {SOURCE_URL}",
        f"State/DC rows: {len(state):,}",
        f"State/DC rows with SAIDI including MED: {len(saidi):,}",
        f"State/DC rows with SAIDI excluding MED: {len(no_med):,}",
        f"Utility-state detail rows: {len(utility):,}",
        f"Utility rows with IEEE SAIDI including MED: {utility.ieee_saidi_with_med_minutes.notna().sum():,}",
        f"Utility rows missing IEEE SAIDI including MED: {utility.ieee_saidi_with_med_minutes.isna().sum():,}",
        "",
        "Highest and lowest state SAIDI, Any Standard (minutes/year):",
        f"With MED highest: {saidi.loc[saidi.saidi_with_med_minutes.idxmax(), 'state']} {saidi.saidi_with_med_minutes.max():,.1f}",
        f"With MED lowest: {saidi.loc[saidi.saidi_with_med_minutes.idxmin(), 'state']} {saidi.saidi_with_med_minutes.min():,.1f}",
        f"Without MED highest: {no_med.loc[no_med.saidi_without_med_minutes.idxmax(), 'state']} {no_med.saidi_without_med_minutes.max():,.1f}",
        f"Without MED lowest: {no_med.loc[no_med.saidi_without_med_minutes.idxmin(), 'state']} {no_med.saidi_without_med_minutes.min():,.1f}",
        "",
        "EIA permits IEEE or other reporting methods. State totals use Any Standard; utility detail uses IEEE values. Missing values are retained as blank, not zero.",
        "State summary values are descriptive and are not adjusted for population, customers, or reporting coverage.",
    ]
    (RESULTS / "analysis_summary.md").write_text("\n".join(report), encoding="utf-8")
    print("Created data/state_totals.csv, data/utility_reliability.csv, and results/analysis_summary.md")


if __name__ == "__main__":
    main()
