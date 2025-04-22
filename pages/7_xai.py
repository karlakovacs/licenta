import time

import streamlit as st
import streamlit.components.v1 as components

from database import *
from utils import *
from xai import *


st.set_page_config(layout="wide", page_title="XAI", page_icon="💡")
nav_bar()
st.title("Explainable AI")


def main():
	modele_antrenate = st.session_state.modele_antrenate
	X_train, X_test = (
		citire_date_temp("X_train"),
		citire_date_temp("X_test"),
	)

	st.session_state.setdefault("grafice_xai", {})

	if not modele_antrenate:
		st.warning("Antrenati modelele mai intai")
		return

	tabs = st.tabs(list(modele_antrenate.keys()))
	for tab, (nume_model, info) in zip(tabs, modele_antrenate.items()):
		with tab:
			st.header(nume_model)

			model = info["model"]
			shap_results = model.get_shap_values(X_train, X_test)
			lime_results = get_explanation(model, X_train, X_test)

			if nume_model not in st.session_state.grafice_xai:
				st.session_state.grafice_xai[nume_model] = {}

			rezultate = st.session_state.grafice_xai[nume_model]

			if shap_results is not None:
				st.subheader("SHAP Bar Plot")
				if "bar" not in rezultate:
					rezultate["bar"] = bar_plot(shap_results)
					time.sleep(1)
				st.pyplot(rezultate["bar"], use_container_width=False)

				st.subheader("SHAP Waterfall Plot")
				if "waterfall" not in rezultate:
					rezultate["waterfall"] = waterfall_plot(shap_results)
					time.sleep(1)
				st.pyplot(rezultate["waterfall"], use_container_width=False)

				st.subheader("SHAP Violin Plot")
				if "violin" not in rezultate:
					rezultate["violin"] = violin_plot(shap_results)
					time.sleep(1)
				st.pyplot(rezultate["violin"], use_container_width=False)

			if lime_results is not None:
				st.subheader("LIME Plot")
				if "lime" not in rezultate:
					rezultate["lime"] = explanation_plot(lime_results)
					time.sleep(1)
				components.html(rezultate["lime"], height=600)


if __name__ == "__main__":
	main()
