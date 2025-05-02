import streamlit as st

from database import creare_raport, incarcare_rapoarte_supabase
from report import generare_raport
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Raport", page_icon="⚡")
nav_bar()
st.title("Generarea raportului")

date_raport = {
	"set_date": st.session_state.get("set_date", None),
	"eda": st.session_state.get("eda", None),
	"procesare": st.session_state.get("procesare", None),
	"modele_antrenate": st.session_state.get("modele_antrenate", None),
	"rezultate_modele": st.session_state.get("rezultate_modele", None),
	"xai": st.session_state.get("xai", None),
	"grafic_comparativ": st.session_state.get("grafic_comparativ", None),
}

if "rapoarte_salvate" not in st.session_state:
	with st.spinner("Generare raport..."):
		html_bytes: bytes = generare_raport(date_raport)
		pdf_bytes: bytes = generare_raport(date_raport, format_pdf=True)
		path = incarcare_rapoarte_supabase(st.session_state.id_utilizator, html_bytes, pdf_bytes)
		creare_raport(st.session_state.id_utilizator, path)
		st.session_state.html_bytes = html_bytes
		st.session_state.pdf_bytes = pdf_bytes
		st.session_state.rapoarte_salvate = True

if "rapoarte_salvate" in st.session_state:
	st.download_button(
		label="📥 Descarcă HTML",
		type="primary",
		data=st.session_state.html_bytes,
		file_name="raport.html",
		mime="text/html",
	)

	st.download_button(
		label="📂 Descarcă PDF",
		type="primary",
		data=st.session_state.pdf_bytes,
		file_name="raport.pdf",
		mime="application/pdf",
	)
