import streamlit as st

from database import create_modele
from dataset import citire_date_temp
from ml import get_hiperparametri, get_model, train_and_test
from ui import *


initializare_pagina("Antrenare", "centered", "Antrenarea modelelor ML", {"modele_selectate": []})


def configurare_hiperparametri(denumire_model: str):
	st.subheader(f"Hiperparametri pentru `{denumire_model}`")

	hiperparametri = get_hiperparametri(denumire_model)
	parametri_utilizator = {}

	for param, detalii in hiperparametri.items():
		key = f"{denumire_model}_{param}"
		help = detalii["help"]

		if detalii["type"] == "numerical":
			parametri_utilizator[param] = st.slider(
				label=param,
				min_value=detalii["min"],
				max_value=detalii["max"],
				value=detalii["default"],
				step=detalii["step"],
				help=help,
				key=key,
			)
		elif detalii["type"] == "categorical":
			parametri_utilizator[param] = st.selectbox(
				label=param,
				options=detalii["values"],
				index=detalii["values"].index(detalii["default"]),
				help=help,
				key=key,
			)
		elif detalii["type"] == "list_numerical":
			parametri_utilizator[param] = []
			n = parametri_utilizator.get("n_layers", len(detalii["default"]))

			for i in range(n):
				val_default = detalii["default"][min(i, len(detalii["default"]) - 1)]
				val = st.slider(
					f"{param} (Strat {i + 1})",
					min_value=detalii["min"],
					max_value=detalii["max"],
					value=val_default,
					step=detalii["step"],
					help=help,
					key=f"{key}_{i}",
				)
				parametri_utilizator[param].append(val)

	return parametri_utilizator


def antrenare_model(denumire_model: str, hiperparametri: dict, X_train, y_train, X_test):
	with st.spinner(f"Se antrenează modelelul `{denumire_model}`..."):
		try:
			model = get_model(denumire_model, hiperparametri, X_train.shape[1])
			is_mlp = True if denumire_model == "Multilayer Perceptron" else False
			durata_antrenare, y_pred, y_prob = train_and_test(
				model,
				X_train,
				y_train,
				X_test,
				is_mlp,
				epochs=hiperparametri.get("epochs", 0),
				batch_size=hiperparametri.get("batch_size", 0),
			)
			st.success(f"`{denumire_model}` antrenat în {durata_antrenare:.2f}s")
			return model, durata_antrenare, y_pred, y_prob
		except Exception as e:
			st.error(f"Eroare la antrenarea `{denumire_model}`: {e}")
			return None, None, None, None


def salvare_modele_in_bd():
	if "ids_modele" not in st.session_state:
		with st.spinner("Stocăm modelele în baza de date..."):
			st.session_state.ids_modele = create_modele(
				st.session_state.id_utilizator, st.session_state.id_set_procesat, st.session_state.modele_antrenate
			)


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
def main():
	modele_selectate = st.session_state.get("modele_selectate", [])
	X_train = citire_date_temp("X_train")
	y_train = citire_date_temp("y_train")
	X_test = citire_date_temp("X_test")

	st.session_state.hiperparametri = {}
	modele_antrenate: dict = {}

	tabs = st.tabs(modele_selectate)

	for i, denumire_model in enumerate(modele_selectate):
		with tabs[i]:
			st.session_state.hiperparametri[denumire_model] = configurare_hiperparametri(denumire_model)

	if st.button("Antrenează modelele", type="primary", disabled="modele_antrenate" in st.session_state):
		for denumire_model in st.session_state.hiperparametri.keys():
			model, durata_antrenare, y_pred, y_prob = antrenare_model(
				denumire_model, st.session_state.hiperparametri[denumire_model], X_train, y_train, X_test
			)
			if model is None:
				continue
			modele_antrenate[denumire_model] = {
				"model": model,
				"durata_antrenare": durata_antrenare,
				"hiperparametri": st.session_state.hiperparametri[denumire_model],
				"y_pred": y_pred,
				"y_prob": y_prob,
			}

		st.session_state.modele_antrenate = modele_antrenate
		if st.session_state.set_date["sursa"] != "Seturi predefinite":
			salvare_modele_in_bd()
		setare_flag("trained_models")
		st.success("Modelele au fost antrenate!")


if __name__ == "__main__":
	main()
