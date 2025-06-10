import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import base64

def plot_csv_bar_chart(csv_str: str) -> str:
    df = pd.read_csv(StringIO(csv_str))
    fig, ax = plt.subplots()
    df.plot(kind="bar", x=df.columns[0], y=df.columns[1], ax=ax)
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
