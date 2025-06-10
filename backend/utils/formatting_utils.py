import pandas as pd
from io import StringIO

def format_csv_to_text(csv_str: str) -> str:
    df = pd.read_csv(StringIO(csv_str))
    return "\n".join([f"- **{row[0]}**: {row[1]:,.2f}" for _, row in df.iterrows()])

def format_csv_to_markdown_table(csv_str: str) -> str:
    df = pd.read_csv(StringIO(csv_str))
    return df.to_markdown(index=False)

def format_csv_to_html_table(csv_str: str) -> str:
    df = pd.read_csv(StringIO(csv_str))
    return df.to_html(index=False, escape=False)
