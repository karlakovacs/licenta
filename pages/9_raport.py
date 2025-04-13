import pandas as pd
import pdfkit
import streamlit as st
import streamlit.components.v1 as components

from database import *
from report import *
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Rulări", page_icon="⚡")
nav_bar()
st.title("Rulari")

config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


def get_df_preprocesari(date: list):
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

	date_filtrate = [
		{chei_preprocesari[cheie]: element[cheie] for cheie in chei_preprocesari if cheie in element}
		for element in date
	]
	df_preprocesari = pd.DataFrame(date_filtrate)
	return df_preprocesari

if "date" not in st.session_state:
	id_utilizator = st.session_state.id_utilizator
	date = get_preprocesari_rulari_grafice(id_utilizator)
	st.session_state.date = date

date = st.session_state.date
df_preprocesari = get_df_preprocesari(date)
# st.dataframe(df_preprocesari, hide_index=True)

html_data = get_raport_html(date, 0)
components.html(html_data, height=600, scrolling=True)

html_bytes = html_data.encode("utf-8")
st.download_button(
	label="Descarcă HTML", data=html_bytes, file_name="raport_rulari.html", mime="text/html"
)

pdf_bytes = pdfkit.from_string(
	html_data,
	False,
	configuration=config,
	)
st.download_button("Descarcă PDF", pdf_bytes, "output.pdf", "application/pdf")
