import pickle

import streamlit as st
import streamlit.components.v1 as components

from report import *
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Rulări", page_icon="⚡")
nav_bar()
st.title("Generarea raportului")

def curatare_modele_antrenate(modele_antrenate: dict) -> dict:
	if modele_antrenate is None:
		return None
	
	modele_curatate = {}

	for denumire_model, info in modele_antrenate.items():
		info_curat = {k: v for k, v in info.items() if k not in ["model", "y_pred", "y_prob"]}
		modele_curatate[denumire_model] = info_curat

	return modele_curatate

### OBTINERE DATE DIN SESSION STATE
date_raport = {
	"set_date": st.session_state.get("set_date", None),
	"eda": st.session_state.get("eda", None),
	"procesare": st.session_state.get("procesare", None),
	"modele_antrenate": curatare_modele_antrenate(st.session_state.get("modele_antrenate", None)),
	"rezultate_modele": st.session_state.get("rezultate_modele", None),
	"xai": st.session_state.get("xai", None),
	"grafic_comparativ": st.session_state.get("grafic_comparativ", None),
}

st.write(date_raport)

with open("date_raport.pkl", "wb") as f:
	pickle.dump(date_raport, f)

# html_data = generare_raport_html(date_raport)
# components.html(html_data, height=600, scrolling=True)

# html_bytes = html_data.encode("utf-8")
# st.download_button(label="Descarcă HTML", data=html_bytes, file_name="raport_rulari.html", mime="text/html")

# pdf_bytes = pdfkit.from_string(
# 	html_data, False, configuration=config, css="C:/Users/karla/Desktop/licenta_app/report/style.css"
# )
# st.download_button("Descarcă PDF", pdf_bytes, "output.pdf", "application/pdf")
