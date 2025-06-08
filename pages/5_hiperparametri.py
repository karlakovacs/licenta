import streamlit as st

from dataset import citire_date_temp
from ml import get_hiperparametri, get_model, train_and_test
from utils import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Hiperparametri", page_icon="assets/logo.png")
nav_bar()
st.title("Configurează hiperparametrii")


modele_selectate = st.session_state.get("modele_selectate", [])
if not modele_selectate:
	st.warning("Selectează mai întâi modelele din pagina anterioară.")
else:
	X_train = citire_date_temp("X_train")
	y_train = citire_date_temp("y_train")
	X_test = citire_date_temp("X_test")

	modele_antrenate = {}

	tabs = st.tabs(modele_selectate)

	for i, denumire_model in enumerate(modele_selectate):
		with tabs[i]:
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

			modele_antrenate[denumire_model] = {
				"model": None,
				"hiperparametri": parametri_utilizator,
				"timp": None,
				"y_pred": None,
				"y_prob": None,
			}

	if st.button("Antrenează modelele", type="primary", disabled="modele_antrenate" in st.session_state):
		# with st.spinner("Se antrenează modelele..."):
		for denumire_model in modele_selectate:
			try:
				date_model = modele_antrenate[denumire_model]
				hiperparametri = date_model["hiperparametri"]
				instanta_model = get_model(denumire_model, hiperparametri, X_train.shape[1])
				if denumire_model == "Multilayer Perceptron":
					timp_antrenare, y_pred, y_prob = train_and_test(
						instanta_model,
						X_train,
						y_train,
						X_test,
						True,
						epochs=hiperparametri["epochs"],
						batch_size=hiperparametri["batch_size"],
					)
				else:
					timp_antrenare, y_pred, y_prob = train_and_test(instanta_model, X_train, y_train, X_test)
				date_model["model"] = instanta_model
				date_model["timp"] = timp_antrenare
				date_model["y_pred"] = y_pred
				date_model["y_prob"] = y_prob
				st.success(f"`{denumire_model}` antrenat în {timp_antrenare:.2f}s")
			except Exception as e:
				st.error(f"Eroare la antrenarea `{denumire_model}`: {e}")
				del modele_antrenate[denumire_model]

		st.session_state.modele_antrenate = modele_antrenate
		st.session_state.get("pagini").update({6: True})
		st.success("Modelele au fost antrenate și salvate!")
		# st.rerun()
