import base64
from io import BytesIO

import matplotlib.figure as plt
import pandas as pd
import plotly.graph_objects as go


def dataframe_to_html(df: pd.DataFrame, format_pdf: bool = False) -> str:
	if format_pdf:
		return df.to_html(border=1)
	else:
		return df.to_html(border=1)


def plotly_to_html(plot: go.Figure, format_pdf: bool = False) -> str:
	if format_pdf:
		img_bytes = plot.to_image(format="svg")
		img_base64 = base64.b64encode(img_bytes).decode("utf-8")
		return f"<img src='data:image/svg+xml;base64,{img_base64}' />"
	else:
		return plot.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})


def matplotlib_to_html(fig: plt.Figure) -> str:
	buf = BytesIO()
	fig.savefig(buf, format="svg", bbox_inches="tight")
	buf.seek(0)
	svg_data = buf.getvalue().decode("utf-8")
	return f"<div>{svg_data}</div>"
