import streamlit as st

from database import create_metrici
from dataset import citire_date_temp
from ml import (
	afisare_metrici,
	calcul_metrici,
	calcul_raport_clasificare,
	plot_curba_pr,
	plot_curba_roc,
	plot_matrice_confuzie,
)
from ui import *


initializare_pagina("Rezultate", "centered", "Rezultatele modelelor ML", {"rezultate_modele": {}})


def salvare_metrici_in_bd():
	if "stocare_metrici" not in st.session_state:
		with st.spinner("Stocăm rezultatele in baza de date..."):
			metrici: dict = {k: v["metrici"] for k, v in st.session_state["rezultate_modele"].items()}
			create_metrici(st.session_state.ids_modele, metrici)
			st.session_state.stocare_metrici = True


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
@require_trained_models
def main():
	modele_antrenate: dict = st.session_state.get("modele_antrenate", None)
	y_test = citire_date_temp("y_test")

	tabs = st.tabs(list(modele_antrenate.keys()))
	for tab, (denumire_model, info) in zip(tabs, modele_antrenate.items()):
		with tab:
			st.header(denumire_model)

			y_pred = info["y_pred"]
			y_prob = info["y_prob"]

			if denumire_model not in st.session_state.rezultate_modele:
				st.session_state.rezultate_modele[denumire_model] = {}

			rezultate = st.session_state.rezultate_modele[denumire_model]

			sectiuni = [
				(
					"Raport de clasificare",
					"raport_clasificare",
					lambda: calcul_raport_clasificare(y_test, y_pred),
					st.write,
				),
				("Metrici", "metrici", lambda: calcul_metrici(y_test, y_pred, y_prob), afisare_metrici),
				(
					"Matrice de confuzie",
					"matrice_confuzie",
					lambda: plot_matrice_confuzie(y_test, y_pred),
					lambda val: st.plotly_chart(val, use_container_width=False, key=f"{denumire_model}_matrice_confuzie"),
				),
				(
					"Curba ROC",
					"roc",
					lambda: plot_curba_roc(y_test, y_prob),
					lambda val: st.plotly_chart(val, use_container_width=False, key=f"{denumire_model}_roc"),
				),
				(
					"Curba PR",
					"pr",
					lambda: plot_curba_pr(y_test, y_prob),
					lambda val: st.plotly_chart(val, use_container_width=False, key=f"{denumire_model}_pr"),
				),
			]

			for titlu, cheie, generator, displayer in sectiuni:
				st.subheader(titlu)
				if cheie not in rezultate:
					rezultate[cheie] = generator()
				displayer(rezultate[cheie])

	salvare_metrici_in_bd()


if __name__ == "__main__":
	main()
