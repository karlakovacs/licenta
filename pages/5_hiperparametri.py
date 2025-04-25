import time

import streamlit as st

from ml import get_model
from utils import citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Hiperparametri", page_icon="⚙️")
nav_bar()
st.title("Configurează hiperparametrii")


def main():
	modele_selectate = st.session_state.get("modele_selectate", [])
	if not modele_selectate:
		st.warning("Selectează mai întâi modelele din pagina anterioară.")
		return

	X_train = citire_date_temp("X_train")
	y_train = citire_date_temp("y_train")
	X_test = citire_date_temp("X_test")

	modele_antrenate = {}

	tabs = st.tabs(modele_selectate)

	for i, nume_model in enumerate(modele_selectate):
		with tabs[i]:
			st.subheader(f"Hiperparametri pentru `{nume_model}`")

			model = get_model(nume_model)
			hyperparams = model.get_hyperparams()
			parametri_utilizator = {}

			for param, detalii in hyperparams.items():
				key = f"{nume_model}_{param}"
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

			model.params = parametri_utilizator
			modele_antrenate[nume_model] = {
				"model": model,
				"params": parametri_utilizator,
				"timp": None,
			}

	if st.button("Antrenează modelele", type="primary"):
		with st.spinner("Se antrenează modelele..."):
			for model in modele_selectate:
				try:
					instanta = modele_antrenate[model]["model"]
					timp = instanta.train_and_test(X_train, y_train, X_test)
					modele_antrenate[model]["timp"] = timp
					st.success(f"`{model}` antrenat în {timp:.2f}s")
				except Exception as e:
					st.error(f"Eroare la `{model}`: {e}")
					del modele_antrenate[model]

			st.session_state.modele_antrenate = modele_antrenate
			st.success("Toate modelele au fost antrenate și salvate!")


if __name__ == "__main__":
	main()
