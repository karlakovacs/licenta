import streamlit as st

from ml import CATEGORII_MODELE, MODELE_HINTURI
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Modele", page_icon="🧠")
nav_bar()
st.title("Modele de Machine Learning & Deep Learning")

st.session_state.setdefault("modele_selectate", [])

st.subheader("Selectează modelele dorite")

modele_selectate = []
for grup in CATEGORII_MODELE:
	categorie = grup["categorie"]
	modele = grup["modele"]

	with st.container(border=True):
		st.subheader(categorie)

		selectii = []
		for model in modele:
			if st.checkbox(model, value=model in st.session_state.modele_selectate, help=MODELE_HINTURI[model], key=f"{categorie}_{model}"):
				selectii.append(model)

		modele_selectate += selectii

if st.button("Salvează selecția", type="primary", use_container_width=True):
	st.session_state.modele_selectate = modele_selectate
	st.toast("Modelele au fost salvate!", icon="✅")
