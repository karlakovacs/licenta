import pickle

import streamlit as st
import streamlit.components.v1 as components

from report import generare_cod_raport, generare_raport


st.set_page_config(page_title="Raport", layout="wide")

if "date_raport" not in st.session_state:
	with open("date_raport.pkl", "rb") as f:
		date_raport = pickle.load(f)
	st.session_state.date_raport = date_raport

date_raport: dict = st.session_state.date_raport

cheie = st.selectbox("Alege", list(date_raport.keys()))
st.subheader(f"`{cheie}`")
st.write(date_raport[cheie])

raport_html = generare_cod_raport(date_raport)
components.html(raport_html, height=600, scrolling=True)

html_bytes = generare_raport(date_raport)
st.download_button(label="Descarcă HTML", data=html_bytes, file_name="raport.html", mime="text/html")

pdf_bytes = generare_raport(date_raport, format_pdf=True)
st.download_button("Descarcă PDF", pdf_bytes, "output.pdf", "application/pdf")
