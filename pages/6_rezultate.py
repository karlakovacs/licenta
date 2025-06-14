import streamlit as st

from database import create_metrici, get_id_utilizator
from dataset import citire_date_temp
from ml import (
	afisare_metrici,
	calcul_metrici,
	calcul_raport_clasificare,
	plot_curba_pr,
	plot_curba_roc,
	plot_matrice_confuzie,
)
from ui import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Rezultate", page_icon="assets/logo.png")
nav_bar()
st.session_state.setdefault("id_utilizator", get_id_utilizator(st.user.sub))

st.title("Rezultate")


def main():
	modele_antrenate: dict = st.session_state.get("modele_antrenate", None)

	if not modele_antrenate:
		st.warning("Antrenati modelele mai intai")
		return

	y_test = citire_date_temp("y_test")

	st.session_state.setdefault("rezultate_modele", {})

	tabs = st.tabs(list(modele_antrenate.keys()))
	for tab, (denumire_model, info) in zip(tabs, modele_antrenate.items()):
		with tab:
			st.header(denumire_model)

			y_pred = info["y_pred"]
			y_prob = info["y_prob"]

			if denumire_model not in st.session_state.rezultate_modele:
				st.session_state.rezultate_modele[denumire_model] = {}

			rezultate = st.session_state.rezultate_modele[denumire_model]

			st.subheader("Raport de clasificare")
			if "raport_clasificare" not in rezultate:
				rezultate["raport_clasificare"] = calcul_raport_clasificare(y_test, y_pred)
			st.write(rezultate["raport_clasificare"])

			st.subheader("Metrici")
			if "metrici" not in rezultate:
				rezultate["metrici"] = calcul_metrici(y_test, y_pred, y_prob)
			afisare_metrici(rezultate["metrici"])

			st.subheader("Matrice de confuzie")
			if "matrice_confuzie" not in rezultate:
				rezultate["matrice_confuzie"] = plot_matrice_confuzie(y_test, y_pred)
			st.plotly_chart(
				rezultate["matrice_confuzie"], use_container_width=False, key=f"{denumire_model}_matrice_confuzie"
			)

			st.subheader("Curba ROC")
			if "roc" not in rezultate:
				rezultate["roc"] = plot_curba_roc(y_test, y_prob)
			st.plotly_chart(rezultate["roc"], use_container_width=False, key=f"{denumire_model}_roc")

			st.subheader("Curba PR")
			if "pr" not in rezultate:
				rezultate["pr"] = plot_curba_pr(y_test, y_prob)
			st.plotly_chart(rezultate["pr"], use_container_width=False, key=f"{denumire_model}_pr")
	
	if "stocare_metrici" not in st.session_state:
		with st.spinner("Stocare rezultate in baza de date..."):
			metrici: dict = {k: v["metrici"] for k, v in st.session_state.rezultate_modele.items()}
			create_metrici(st.session_state.ids_modele, metrici)
			st.session_state.stocare_metrici = True


if __name__ == "__main__":
	main()
