import streamlit as st

from ui import *
from ui import CATEGORII_MODELE, MODELE_HINTURI


initializare_pagina("Modele ML", "wide", "Modele de Machine Learning", {"modele_selectate": []})


@require_auth
@require_selected_dataset
@require_processed_dataset
def main():
	st.subheader("Selectează modelele dorite")

	col1, col2 = st.columns([1, 4])
	with col1:
		selecteaza_toate = st.button("Selectează toate modelele", type="primary")
	with col2:
		curata_selectia = st.button("Curăță selecția", type="tertiary")

	if selecteaza_toate:
		st.session_state.modele_selectate = [model for grup in CATEGORII_MODELE for model in grup["modele"]]
	elif curata_selectia:
		st.session_state.modele_selectate = []

	modele_session_state = obtinere_cheie("modele_selectate", [])
	modele_selectate = []

	for grup in CATEGORII_MODELE:
		categorie = grup["categorie"]
		modele = grup["modele"]

		with st.container(border=True):
			st.subheader(categorie)

			selectii = []
			for model in modele:
				bifat = model in modele_session_state
				if st.checkbox(
					model,
					value=bifat,
					help=MODELE_HINTURI[model],
					key=f"{categorie}_{model}",
				):
					selectii.append(model)

			modele_selectate += selectii

	if st.button("Salvează selecția", type="primary", disabled=verificare_flag("selected_models")):
		st.session_state.modele_selectate = modele_selectate
		setare_flag("selected_models")
		st.toast("Modelele au fost selectate!", icon="✅")


if __name__ == "__main__":
	main()
