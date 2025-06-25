import streamlit as st

from database import create_raport
from report import generare_raport
from storage import upload_report_to_storage
from ui import *


initializare_pagina("Raport", "wide", "Generarea raportului")


def creare_date_raport():
	keys = [
		"set_date",
		"eda",
		"procesare",
		"modele_antrenate",
		"rezultate_modele",
		"comparatii_modele",
		"instante_test",
		"xai_test",
		"instante_predictii",
		"xai_predictii",
	]
	date_raport = {key: st.session_state.get(key, None) for key in keys}
	return date_raport


@require_auth
@require_selected_dataset
def main():
	st.session_state.date_raport = creare_date_raport()

	# html_bytes: bytes = generare_raport(st.session_state.date_raport)
	# st.components.v1.html(html_bytes.decode("utf-8"), height=800, scrolling=True)
	# st.download_button(label="Descarcă raportul HTML", data=html_bytes, file_name="raport.html", mime="text/html")

	if "raport_generat" not in st.session_state:
		with st.spinner("Generare raport..."):
			html_bytes: bytes = generare_raport(st.session_state.date_raport)
			url, data_generare = upload_report_to_storage(st.session_state.id_utilizator, html_bytes)
			create_raport(st.session_state.id_utilizator, url, data_generare)
			st.session_state.html_bytes = html_bytes
			st.session_state.raport_generat = True

	if "raport_generat" in st.session_state:
		st.download_button(
			label="📥 Descarcă raportul HTML",
			type="primary",
			data=st.session_state.html_bytes,
			file_name="raport.html",
			mime="text/html",
		)


if __name__ == "__main__":
	main()
