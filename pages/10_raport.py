import streamlit as st

from report import generare_raport
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
	date_raport = {key: st.session_state.get(key) for key in keys}
	return date_raport


@require_auth
@require_selected_dataset
def main():
	st.session_state.date_raport = creare_date_raport()

	html_bytes: bytes = generare_raport(st.session_state.date_raport)
	st.components.v1.html(html_bytes.decode("utf-8"), height=800, scrolling=True)

	st.download_button(label="Descarcă raportul HTML", data=html_bytes, file_name="raport.html", mime="text/html")

	# if "rapoarte_salvate" not in st.session_state:
	# 	with st.spinner("Generare raport..."):
	# 		html_bytes: bytes = generare_raport(st.session_state.date_raport)
			# pdf_bytes: bytes = generare_raport(st.session_state.date_raport, format_pdf=True)
			# path = incarcare_rapoarte_supabase(st.session_state.id_utilizator, html_bytes, pdf_bytes)
			# creare_raport(st.session_state.id_utilizator, path)
			# st.session_state.html_bytes = html_bytes
			# st.session_state.pdf_bytes = pdf_bytes
			# st.session_state.rapoarte_salvate = True

	# if "rapoarte_salvate" in st.session_state:
	# 	st.download_button(
	# 		label="📥 Descarcă HTML",
	# 		type="primary",
	# 		data=st.session_state.html_bytes,
	# 		file_name="raport.html",
	# 		mime="text/html",
	# 	)

	# 	st.download_button(
	# 		label="📂 Descarcă PDF",
	# 		type="primary",
	# 		data=st.session_state.pdf_bytes,
	# 		file_name="raport.pdf",
	# 		mime="application/pdf",
	# 	)


if __name__ == "__main__":
	main()
