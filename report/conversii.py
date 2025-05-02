import base64
from io import BytesIO

import matplotlib.figure as plt
import pandas as pd
import plotly.graph_objects as go


def dataframe_to_html(df: pd.DataFrame, format_pdf: bool = False) -> str:
	table_html = df.to_html(classes="dataframe", index=False)

	if format_pdf:
		return table_html
	else:
		return f"""
        <div class="scrollable-table">
            {table_html}
        </div>
        """


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
