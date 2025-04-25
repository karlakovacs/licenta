import time

import streamlit as st
import streamlit.components.v1 as components

from utils import citire_date_temp, nav_bar
from xai import *


st.set_page_config(layout="wide", page_title="XAI", page_icon="💡")
nav_bar()
st.title("Explainable AI")


def main():
	modele_antrenate = st.session_state.get("modele_antrenate", {})
	X_train, X_test = (
		citire_date_temp("X_train"),
		citire_date_temp("X_test"),
	)

	if not modele_antrenate:
		st.warning("Antrenează modelele mai întâi.")
		return

	st.session_state.setdefault("xai", {})
	optiuni_modele = list(modele_antrenate.keys())
	nume_model = st.selectbox("Selectează modelul pentru care vrei să vezi analiza XAI", optiuni_modele)

	if nume_model:
		st.header(nume_model)

		info = modele_antrenate[nume_model]
		model = info["model"]

		if nume_model not in st.session_state.xai:
			st.session_state.xai[nume_model] = {
				"shap": {"values": None, "plots": {}},
				"lime": {"explanation": None, "plot": None},
				"dice": {""}
			}

		grafice_model = st.session_state.xai[nume_model]
		shap_dict = grafice_model["shap"]
		lime_dict = grafice_model["lime"]

		if shap_dict["values"] is None:
			shap_dict["values"] = calculate_shap_values(model, X_train, X_test)
			time.sleep(5)

		if shap_dict["values"] is not None:
			st.subheader("SHAP Bar Plot")
			if "bar" not in shap_dict["plots"]:
				shap_dict["plots"]["bar"] = bar_plot(shap_dict["values"])
				time.sleep(5)
			st.pyplot(shap_dict["plots"]["bar"], use_container_width=False)

			st.subheader("SHAP Waterfall Plot")
			if "waterfall" not in shap_dict["plots"]:
				shap_dict["plots"]["waterfall"] = waterfall_plot(shap_dict["values"])
				time.sleep(5)
			st.pyplot(shap_dict["plots"]["waterfall"], use_container_width=False)

			st.subheader("SHAP Violin Plot")
			if "violin" not in shap_dict["plots"]:
				shap_dict["plots"]["violin"] = violin_plot(shap_dict["values"])
				time.sleep(5)
			st.pyplot(shap_dict["plots"]["violin"], use_container_width=False)

		if lime_dict["explanation"] is None:
			lime_dict["explanation"] = get_explanation(model, X_train, X_test)
			time.sleep(5)

		if lime_dict["explanation"] is not None:
			st.subheader("LIME Plot")
			if lime_dict["plot"] is None:
				lime_dict["plot"] = explanation_plot(lime_dict["explanation"])
				time.sleep(5)
			components.html(lime_dict["plot"], height=600)


if __name__ == "__main__":
	main()
