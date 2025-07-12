import base64
import copy
from io import BytesIO
import re

import matplotlib.figure as plt
import pandas as pd
import plotly.graph_objects as go


def dataframe_to_html(df: pd.DataFrame, index: bool = False) -> str:
	table_html = df.to_html(classes="dataframe", index=index)
	return table_html


def plotly_to_html(plot: go.Figure) -> str:
	fig = copy.deepcopy(plot)
	plot.update_layout(
		template="plotly_dark", paper_bgcolor="#1e1e1e", plot_bgcolor="#1e1e1e", font=dict(color="#FFFFFF")
	)
	plot.update_xaxes(color="#FFFFFF", gridcolor="#444")
	plot.update_yaxes(color="#FFFFFF", gridcolor="#444")
	return plot.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})


def matplotlib_to_html(fig: plt.Figure) -> str:
	buf = BytesIO()
	fig.savefig(buf, format="svg", bbox_inches="tight")
	buf.seek(0)
	svg_data = buf.getvalue().decode("utf-8")
	return f"<div>{svg_data}</div>"


def explicatii_dice_to_text(explicatii: dict) -> str:
	if not explicatii:
		return "<p><i>Nu există explicații disponibile pentru acest contrafactual.</i></p>"

	rezultat = "<ol>"
	for idx, modificari in explicatii.items():
		rezultat += f"<li><b>Contrafactual #{idx + 1}</b></li>"
		rezultat += "<ul>"

		for m in modificari:
			variabila = m.get("variabila", "necunoscută")
			valoare = m.get("valoare", "?")
			tip = m.get("tip")
			directie = m.get("directie")

			if tip == "numeric":
				sens = "crească" if directie == "+" else "scadă"
				rezultat += f"<li><b>{variabila}</b> trebuie să {sens} cu <code>{valoare}</code></li>"
			else:
				rezultat += f"<li><b>{variabila}</b> trebuie să aibă valoarea <code>{valoare}</code></li>"

		rezultat += "</ul>"
	rezultat += "</ol>"
	return rezultat


def markdown_to_html(text: str) -> str:
	lines = text.strip().split("\n")
	html_lines = []
	in_list = False

	for line in lines:
		line = line.strip()

		if line.startswith("- "):
			if not in_list:
				html_lines.append("<ul>")
				in_list = True
			content = line[2:]
		else:
			if in_list:
				html_lines.append("</ul>")
				in_list = False
			content = line

		content = re.sub(r"`([^`]+)`", r"<code>\1</code>", content)

		content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)

		content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", content)

		if line.startswith("- "):
			html_lines.append(f"<li>{content}</li>")
		else:
			html_lines.append(f"<p>{content}</p>")

	if in_list:
		html_lines.append("</ul>")

	return "\n".join(html_lines)


def image_to_html(url: str):
	with open(url, "rb") as f:
		encoded = base64.b64encode(f.read()).decode()
	return f'<img src="data:image/png;base64,{encoded}" class="logo">'
