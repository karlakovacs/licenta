import streamlit as st

from ml import (
	afisare_metrici,
	calcul_metrici,
	calcul_raport_clasificare,
	plot_curba_pr,
	plot_curba_roc,
	plot_matrice_confuzie,
)
from utils import citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Rezultate", page_icon="🎯")
nav_bar()
st.title("Rezultate")


def main():
	modele_antrenate: dict = st.session_state.get("modele_antrenate", None)

	if not modele_antrenate:
		st.warning("Antrenati modelele mai intai")
		return

	y_test = citire_date_temp("y_test")

	st.session_state.setdefault("rezultate_modele", {})

	tabs = st.tabs(list(modele_antrenate.keys()))
	for tab, (nume_model, info) in zip(tabs, modele_antrenate.items()):
		with tab:
			st.header(nume_model)

			model = info["model"]
			y_pred = model.y_pred
			y_prob = model.y_prob

			if nume_model not in st.session_state.rezultate_modele:
				st.session_state.rezultate_modele[nume_model] = {}

			rezultate = st.session_state.rezultate_modele[nume_model]

			st.subheader("Raport de clasificare")
			if "raport_clasificare" not in rezultate:
				rezultate["raport_clasificare"] = calcul_raport_clasificare(y_test, y_pred)
			st.write(rezultate["raport_clasificare"])

			st.subheader("Metrici")
			if "metrici" not in rezultate:
				rezultate["metrici"] = calcul_metrici(y_test, y_pred, y_prob, nume_model)
			afisare_metrici(rezultate["metrici"])

			st.subheader("Matrice de confuzie")
			if "matrice_confuzie" not in rezultate:
				rezultate["matrice_confuzie"] = plot_matrice_confuzie(y_test, y_pred, nume_model)
			st.plotly_chart(rezultate["matrice_confuzie"], use_container_width=False)

			st.subheader("Curba ROC")
			if "roc" not in rezultate:
				rezultate["roc"] = plot_curba_roc(y_test, y_prob, nume_model)
			st.plotly_chart(rezultate["roc"], use_container_width=False)

			st.subheader("Curba PR")
			if "pr" not in rezultate:
				rezultate["pr"] = plot_curba_pr(y_test, y_prob, nume_model)
			st.plotly_chart(rezultate["pr"], use_container_width=False)


if __name__ == "__main__":
	main()
