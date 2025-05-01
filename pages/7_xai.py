import traceback

import streamlit as st
import streamlit.components.v1 as components

from utils import citire_date_temp, nav_bar
from xai import *


st.set_page_config(layout="wide", page_title="XAI", page_icon="💡")
nav_bar()
st.title("Explainable AI")


modele_antrenate = st.session_state.get("modele_antrenate", {})
X_train, X_test, y_train = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_train"),
)

if not modele_antrenate:
	st.warning("Antrenează modelele mai întâi.")

else:
	# st.session_state.setdefault("xai", {})
	st.session_state["xai"] = {}
	optiuni_modele = list(modele_antrenate.keys())

	denumire_model = st.selectbox(
		"Alege modelul pentru care vrei să vezi analiza explicațiilor",
		optiuni_modele,
		key="model_xai",
		help="Selectează modelul de machine learning asupra căruia vrei să aplici metodele XAI.",
	)

	tehnici_xai = ["SHAP", "LIME", "DiCE ML"]
	tehnica_xai = st.selectbox(
		"Alege tehnica de explicație (XAI)",
		tehnici_xai,
		key="tehnica_xai",
		help="Selectează tehnica de explainable AI (XAI) pentru a interpreta deciziile modelului ales.",
	)

	nr_instante = (
		len(X_test)
		if denumire_model
		not in ["Quadratic Discriminant Analysis", "K-Nearest Neighbors", "Support Vector Classifier", "AdaBoost"]
		else 50
	)

	instanta_xai = st.slider(
		"Selectează exemplul de test pentru analiză",
		min_value=0,
		max_value=nr_instante - 1,
		value=0,
		key="instanta_xai",
		help="Alege indexul exemplului de test pentru care dorești să generezi explicații contrafactuale sau de importanță a caracteristicilor.",
	)

if denumire_model and tehnica_xai:
	st.header(f"Analiză {tehnica_xai} pentru modelul `{denumire_model}`")

	model = modele_antrenate[denumire_model]["model"]

	st.session_state["xai"] = {}
	st.session_state["xai"].setdefault(denumire_model, {})

	if tehnica_xai == "SHAP":
		if denumire_model not in ["Decision Tree", "Random Forest", "Balanced Random Forest", "AdaBoost"]:
			st.session_state["xai"][denumire_model].setdefault("shap", {"values": None, "plots": {}})
			shap_data = st.session_state["xai"][denumire_model]["shap"]
			if shap_data["values"] is None:
				with st.spinner("Calculăm valorile SHAP..."):
					shap_data["values"] = calculate_shap_values(model, X_train, X_test)

			if shap_data["values"] is not None:
				st.subheader("📊 Bar Plot")
				if "bar" not in shap_data["plots"]:
					shap_data["plots"]["bar"] = bar_plot(shap_data["values"])
				if shap_data["plots"]["bar"]:
					st.pyplot(shap_data["plots"]["bar"], use_container_width=False)
				else:
					st.info("Nu s-a putut genera graficul Bar Plot.")

				st.subheader("🎻 Violin Plot")
				if "violin" not in shap_data["plots"]:
					shap_data["plots"]["violin"] = violin_plot(shap_data["values"])
				if shap_data["plots"]["violin"]:
					st.pyplot(shap_data["plots"]["violin"], use_container_width=False)
				else:
					st.info("Nu s-a putut genera graficul Violin Plot.")

				st.subheader(f"🌊 Waterfall Plot (instanța {instanta_xai})")
				if "waterfall" not in shap_data["plots"]:
					shap_data["plots"]["waterfall"] = {}
				if instanta_xai not in shap_data["plots"]["waterfall"]:
					shap_data["plots"]["waterfall"][instanta_xai] = waterfall_plot(shap_data["values"], instanta_xai)
				if shap_data["plots"]["waterfall"][instanta_xai]:
					st.pyplot(shap_data["plots"]["waterfall"][instanta_xai], use_container_width=False)
				else:
					st.info("Nu s-a putut genera graficul Waterfall Plot.")
			else:
				st.info("Nu s-au putut calcula valorile SHAP.")
		else:
			st.info(f"Analiza SHAP este indisponbilă pentru modelul `{denumire_model}`.")

	elif tehnica_xai == "LIME":
		lime_data = st.session_state["xai"][denumire_model].setdefault("lime", {"explanations": {}})

		if instanta_xai not in lime_data["explanations"]:
			with st.spinner("Generăm explicația LIME..."):
				lime_data["explanations"][instanta_xai] = get_explanation(model, X_train, X_test, instanta_xai)

		st.subheader(f"📈 Explicație locală pentru instanța {instanta_xai}")
		if lime_data["explanations"][instanta_xai] is not None:
			components.html(explanation_plot(lime_data["explanations"][instanta_xai]), height=600)
			st.pyplot(explanation_pyplot(lime_data["explanations"][instanta_xai]))
			st.write(lime_data["explanations"][instanta_xai].as_list())
		else:
			st.info("Nu s-a putut genera explicația LIME.")

	elif tehnica_xai == "DiCE ML":
		# st.session_state["xai"][denumire_model].setdefault("dice", {"explainer": None, "counterfactuals": {}})

		st.session_state["xai"][denumire_model] = {"dice": {"explainer": None, "counterfactuals": {}}}

		dice_data = st.session_state["xai"][denumire_model]["dice"]

		tinta = st.session_state.set_date["tinta"]
		date_instanta = X_test.iloc[[instanta_xai]]

		st.subheader("Exemplu selectat")
		st.write(date_instanta)

		if dice_data["explainer"] is None:
			with st.spinner("Creăm explainerul DiCE..."):
				dice_data["explainer"] = get_dice_explainer(model, X_train, y_train, tinta)

		counterfactuals = dice_data["counterfactuals"]

		if instanta_xai not in counterfactuals:
			with st.spinner("Generăm explicații contrafactuale..."):
				predictie, cf_df, explicatii = calculate_counterfactuals(
					model, dice_data["explainer"], date_instanta, X_train.columns.tolist()
				)
				counterfactuals[instanta_xai] = {
					"predictie": predictie,
					"cf_df": cf_df,
					"explicatii": explicatii,
				}

		rezultate: dict = counterfactuals[instanta_xai]
		predictie, cf_df, explicatii = rezultate.values()
		if not any(rezultate.get(k) is None for k in ["predictie", "cf_df", "explicatii"]):
			st.subheader(f"🔮 Predicția modelului `{denumire_model}`: `{predictie}`")

			st.subheader("🍎 Modificări minime pentru a schimba predicția modelului")
			st.dataframe(cf_df)

			st.subheader("🔍 Intepretări")
			st.write(interpretare_explicatii(explicatii))
		else:
			st.info("Nu s-au putut genera explicațiile DiCE ML.")
			# st.error(f"Eroare la generarea explicațiilor pentru `{denumire_model}`: {e}")
			# st.code(traceback.format_exc(), language="python")
