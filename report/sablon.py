import plotly.io as pio
import streamlit as st

from database.stocare import *


SUPABASE_BASE_URL = st.secrets.supabase.SUPABASE_BASE_URL


def get_raport_html(date: list, index: int):
	preprocesare: dict = date[index]
	# st.json(preprocesare)

	chei_preprocesari = {
		"set_date": "Set de date",
		"optiune_selectie": "Selecție caracteristici",
		"nr_variabile": "Număr variabile",
		"optiune_dezechilibru": "Strategie dezechilibru",
		"optiune_scalare": "Metodă de scalare",
		"dimensiune_test": "Dimensiune test",
		"stratificat": "Împărțire stratificată?",
		"created_at": "Dată creare",
	}

	html = """
	<html>
	<head>
		<meta charset="utf-8">
		<title>Raport</title>
		<style>
			body { font-family: 'Arial', sans-serif; background-color: grey; text-align: center }
			h1 {{ color: #333; }}
			table { width: 100%; border-collapse: collapse; margin-top: 20px; }
			th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
			th { background-color: #f2f2f2; }
			img {{ width: 80%; margin: 20px auto; }}
			.rulare { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }
		</style>
	</head>
	<body>
		<h1>Raport</h1>
		<table>
			<tr><th>Categorie</th><th>Valoare</th></tr>
	"""

	for key, label in chei_preprocesari.items():
		value = preprocesare.get(key, "N/A")
		html += f"<tr><td>{label}</td><td>{value}</td></tr>"
	html += "</table>"

	rulari: list = preprocesare.get("rulari", [])
	for rulare in rulari:
		html += """
		<div class='rulare'>
			<h3>Model: {model}</h3>
			<p><strong>Timp execuție:</strong> {timp_executie:.4f} secunde</p>
			<h4>Metrici:</h4>
			<table>
				<tr><th>Metrică</th><th>Valoare</th></tr>
		""".format(
			model=rulare.get("model", "N/A"),
			timp_executie=rulare.get("timp_executie", 0),
		)

		for metrica, valoare in rulare.get("metrici", {}).items():
			html += f"<tr><td>{metrica}</td><td>{valoare:.4f}</td></tr>"

		html += """
			</table>
			<h4>Hiperparametri:</h4>
			<table>
				<tr><th>Parametru</th><th>Valoare</th></tr>
		"""

		for param, valoare in rulare.get("hiperparametri", {}).items():
			valoare = valoare if valoare is not None else "N/A"
			html += f"<tr><td>{param}</td><td>{valoare}</td></tr>"

		html += """
			</table>
			<h4>Grafice:</h4>
		"""

		for grafic in rulare.get("grafice", []):
			tip = grafic.get("tip", "N/A")
			url = SUPABASE_BASE_URL + grafic.get("url", "")
			html += f"<p><strong>{tip}:</strong></p>"

			if url.endswith(".png") or url.endswith(".svg"):
				html += f"<img src='{url}' alt='{tip}'>"
			elif url.endswith(".html"):
				html += f"<iframe src='{url}' width='100%' height='500px' style='border:none;'></iframe>"
			elif url.endswith(".json"):
				try:
					response = requests.get(url)
					if response.status_code == 200:
						fig_json = response.json()
						fig_html = pio.to_html(fig_json, full_html=False, include_plotlyjs="cdn")
						html += fig_html
					else:
						html += f"<p style='color:red;'>Eroare la descărcarea JSON: {response.status_code}</p>"
				except Exception as e:
					html += f"<p style='color:red;'>Eroare la încărcarea graficului Plotly: {str(e)}</p>"

		html += """
		</div>
		"""

	html += """
	</body>
	</html>
	"""

	return html
