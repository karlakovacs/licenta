import streamlit as st
import streamlit.components.v1 as components

from report import *
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Raport", page_icon="⚡")
nav_bar()
st.title("Generarea raportului")

# def curatare_modele_antrenate(modele_antrenate: dict) -> dict:
# 	if modele_antrenate is None:
# 		return None
	
# 	modele_curatate = {}

# 	for denumire_model, info in modele_antrenate.items():
# 		info_curat = {k: v for k, v in info.items() if k not in ["model", "y_pred", "y_prob"]}
# 		modele_curatate[denumire_model] = info_curat

# 	return modele_curatate

### OBTINERE DATE DIN SESSION STATE
date_raport = {
	"set_date": st.session_state.get("set_date", None),
	"eda": st.session_state.get("eda", None),
	"procesare": st.session_state.get("procesare", None),
	"modele_antrenate": st.session_state.get("modele_antrenate", None),
	"rezultate_modele": st.session_state.get("rezultate_modele", None),
	"xai": st.session_state.get("xai", None),
	"grafic_comparativ": st.session_state.get("grafic_comparativ", None),
}

raport_html = generare_cod_raport(date_raport)
components.html(raport_html, height=600, scrolling=True)

html_bytes = generare_raport(date_raport)
st.download_button(label="Descarcă HTML", data=html_bytes, file_name="raport.html", mime="text/html")

pdf_bytes = generare_raport(date_raport, format_pdf=True)
st.download_button("Descarcă PDF", pdf_bytes, "raport.pdf", "application/pdf")
