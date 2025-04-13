import streamlit as st

from ml import MODELE
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Modele", page_icon="🧠")
nav_bar()
st.title("Modele de ML și DL")

if "modele_selectate" not in st.session_state:
	st.session_state.modele_selectate = []

modele_selectate = []

for grup in MODELE:
	categorie = grup["categorie"]
	modele = grup["modele"]

	selectii = st.pills(
		f"**{categorie}**",
		options=modele,
		selection_mode="multi",
		default=[model for model in modele if model in st.session_state.modele_selectate],
	)

	modele_selectate += selectii

st.write(modele_selectate)

if st.button("Selectare"):
	st.session_state.modele_selectate = modele_selectate
	st.success("Modelele au fost salvate!")
