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
					"Afișează precizia (`precision`), acuratețea (`accuracy`), sensibilitatea (`recall`) și scorul F1 pentru fiecare clasă.\n\n"
					"Este util pentru a înțelege performanța modelului asupra fiecărei clase în parte, mai ales în cazul claselor dezechilibrate.",
					"raport_clasificare",
					lambda: calcul_raport_clasificare(y_test, y_pred),
					st.write,
				),
				(
					"Metrici",
					"Afișează metrici esențiale pentru a evalua cât de bine generalizează modelul.",
					"metrici",
					lambda: calcul_metrici(y_test, y_pred, y_prob),
					afisare_metrici,
				),
				(
					"Matrice de confuzie",
					"Este o diagramă care arată câte instanțe au fost prezise corect ca pozitive/negative, sau clasificate greșit.\n\n"
					"Este extrem de utilă pentru a înțelege tipul de erori făcute de model (false pozitive vs. false negative).\n\n"
					"Valorile de pe diagonala principală (stânga sus și dreapta jos) ar trebui să fie cât mai mari, indicând predicții corecte. Celulele din afara diagonalei (erori) trebuie să fie cât mai aproape de zero.",
					"matrice_confuzie",
					lambda: plot_matrice_confuzie(y_test, y_pred),
					lambda val: st.plotly_chart(
						val, use_container_width=False, key=f"{denumire_model}_matrice_confuzie"
					),
				),
				(
					"Curba ROC",
					"Arată trade-off-ul dintre rata de true positive (Recall) și rata de false positive, în funcție de pragul de decizie.\n\n"
					"Este importantă în probleme cu clase dezechilibrate, cazuri unde costul fals-pozitivelor trebuie redus.\n\n"
					"AUC-ROC (aria de sub curbă) este un indicator global al capacității modelului de a separa clasele.\n\n"
					"Curba trebuie să urce abrupt spre colțul stânga sus, apoi să continue aproape orizontal. Acest fapt indică o rată mare de `true positives` cu un număr minim de `false positives`.",
					"roc",
					lambda: plot_curba_roc(y_test, y_prob),
					lambda val: st.plotly_chart(val, use_container_width=False, key=f"{denumire_model}_roc"),
				),
				(
					"Curba PR",
					"Prezintă relația dintre precision și recall, variind pragul de decizie.\n\n"
					"Este mai informativă decât ROC în cazuri dezechilibrate (ex: doar 1% clasa pozitivă), pentru că se concentrează pe performanța modelului asupra clasei pozitive.\n\n"
					"Curba trebuie să fie cât mai aproape de colțul dreapta sus, ceea ce înseamnă că modelul păstrează o precizie ridicată chiar și când acoperă majoritatea cazurilor pozitive (`recall` mare).",
					"pr",
					lambda: plot_curba_pr(y_test, y_prob),
					lambda val: st.plotly_chart(val, use_container_width=False, key=f"{denumire_model}_pr"),
				),
			]

			for titlu, help, cheie, generator, displayer in sectiuni:
				st.subheader(titlu, help=help)
				if cheie not in rezultate:
					rezultate[cheie] = generator()
				displayer(rezultate[cheie])

	if st.session_state.set_date["sursa"] != "Seturi predefinite":
		salvare_metrici_in_bd()


if __name__ == "__main__":
	main()
