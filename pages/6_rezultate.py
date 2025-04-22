import streamlit as st

from ml import (
	afisare_metrici,
	afisare_raport_clasificare,
	calcul_metrici,
	plot_curba_pr,
	plot_curba_roc,
	plot_matrice_confuzie,
)
from utils import citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Rezultate", page_icon="🎯")
nav_bar()
st.title("Rezultate")

modele_antrenate = st.session_state.modele_antrenate
X_train, X_test, y_test = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_test"),
)

for key in ["matrici_confuzie", "curbe_roc", "curbe_pr", "metrici_modele"]:
	st.session_state.setdefault(key, {})

tabs = st.tabs([key for key in modele_antrenate])
for tab, (key, model) in zip(tabs, modele_antrenate.items()):
	with tab:
		st.header(key)
		y_pred = model.y_pred
		y_prob = model.y_prob

		st.subheader("Raport de clasificare")
		afisare_raport_clasificare()

		st.subheader("Metrici")
		if key not in st.session_state.metrici_modele:
			calcul_metrici(y_test, y_pred, y_prob, key)
		afisare_metrici(st.session_state.metrici_modele[key])

		st.subheader("Matrice de confuzie")
		if key not in st.session_state.matrici_confuzie:
			plot_matrice_confuzie(y_test, y_pred, key)
		st.plotly_chart(st.session_state.matrici_confuzie[key], use_container_width=False)

		st.subheader("Curba ROC")
		if key not in st.session_state.curbe_roc:
			plot_curba_roc(y_test, y_prob, key)
		st.plotly_chart(st.session_state.curbe_roc[key], use_container_width=False)

		st.subheader("Curba PR")
		if key not in st.session_state.curbe_pr:
			plot_curba_pr(y_test, y_prob, key)
		st.plotly_chart(st.session_state.curbe_pr[key], use_container_width=False)
