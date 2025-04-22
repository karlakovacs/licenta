import concurrent.futures

import streamlit as st

from ml import get_model
from utils import citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Hiperparametri", page_icon="⚙️")
nav_bar()
st.title("Configurează hiperparametrii")

modele_selectate = st.session_state.get("modele_selectate", [])
if not modele_selectate:
	st.warning("Selectează mai întâi modelele din pagina anterioară.")
	st.stop()

X_train = citire_date_temp("X_train")
y_train = citire_date_temp("y_train")
X_test = citire_date_temp("X_test")
y_test = citire_date_temp("y_test")

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
		with concurrent.futures.ThreadPoolExecutor() as executor:
			futures = {
				executor.submit(modele_antrenate[model]["model"].train, X_train, y_train, X_test, y_test): model
				for model in modele_selectate
			}

			for future in concurrent.futures.as_completed(futures):
				nume = futures[future]
				try:
					timp = future.result()
					modele_antrenate[nume]["timp"] = timp
					st.success(f"`{nume}` antrenat în {timp:.2f}s")

				except Exception as e:
					st.error(f"Eroare la `{nume}`: {e}")
					del modele_antrenate[nume]

		st.session_state.modele_antrenate = modele_antrenate
		st.success("Toate modelele au fost antrenate și salvate!")
