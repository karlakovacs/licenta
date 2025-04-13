import concurrent.futures

import streamlit as st

from ml import get_model
from utils import citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Hiperparametri", page_icon="⚙️")
st.title("Hiperparametri")
nav_bar()

hiperparametri = {}
instante_modele = {}
timpi_executie = {}
X_train, y_train, X_test, y_test = (
	citire_date_temp("X_train"),
	citire_date_temp("y_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_test"),
)

if "modele_selectate" in st.session_state:
	modele_selectate = st.session_state.modele_selectate
	tabs = st.tabs(modele_selectate)
	for i, model_selectat in enumerate(modele_selectate):
		with tabs[i]:
			instanta_model = get_model(model_selectat)
			hiperparametri[model_selectat] = instanta_model.get_params_utilizator()
			instante_modele[model_selectat] = instanta_model

	train_button = st.button("Antrenează modelele")

	if train_button and modele_selectate:
		modele_antrenate = {}

		with st.spinner("Se antrenează modelele..."):
			with concurrent.futures.ThreadPoolExecutor() as executor:
				future_to_model = {
					executor.submit(
						instante_modele[model].train, X_train, y_train, X_test, y_test
					): model
					for model in modele_selectate
				}

				for future in concurrent.futures.as_completed(future_to_model):
					nume_model = future_to_model[future]
					try:
						timp_executie = future.result()
						timpi_executie[nume_model] = timp_executie
						modele_antrenate[nume_model] = instante_modele[nume_model]

						st.success(f"{nume_model} antrenat! (⏳ {timp_executie:.2f}s)")
					except Exception as e:
						del hiperparametri[nume_model]
						st.error(f"Eroare la antrenarea modelului {nume_model}: {e}")
		st.session_state.hiperparametri = hiperparametri
		st.session_state.timpi_executie = timpi_executie
		st.session_state.modele_antrenate = modele_antrenate
else:
	st.warning("Alegeti modelele!")
