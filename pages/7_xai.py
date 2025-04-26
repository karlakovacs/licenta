import streamlit as st
import streamlit.components.v1 as components

from utils import citire_date_temp, nav_bar
from xai import *


st.set_page_config(layout="wide", page_title="XAI", page_icon="💡")
nav_bar()
st.title("Explainable AI")

def highlight_positive_negative(val):
    if val > 0:
        return "background-color: lightgreen; color: black;"
    elif val < 0:
        return "background-color: salmon; color: black;"
    else:
        return ""


modele_antrenate = st.session_state.get("modele_antrenate", {})
X_train, X_test, y_train = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_train"),
)

if not modele_antrenate:
	st.warning("Antrenează modelele mai întâi.")

else:
	st.session_state.setdefault("xai", {})
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
		if denumire_model not in ["Quadratic Discriminant Analysis", "K-Nearest Neighbors", "Support Vector Classifier"]
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

	st.session_state["xai"].setdefault(denumire_model, {})

	if tehnica_xai == "SHAP":
		st.session_state["xai"][denumire_model].setdefault("shap", {"values": None, "plots": {}})
		shap_data = st.session_state["xai"][denumire_model]["shap"]
		if shap_data["values"] is None:
			with st.spinner("Calculăm valorile SHAP..."):
				shap_data["values"] = calculate_shap_values(model, X_train, X_test)

		if shap_data["values"] is not None:
			st.subheader("📊 Bar Plot")
			if "bar" not in shap_data["plots"]:
				shap_data["plots"]["bar"] = bar_plot(shap_data["values"])
			st.pyplot(shap_data["plots"]["bar"], use_container_width=False)

			st.subheader("🎻 Violin Plot")
			if "violin" not in shap_data["plots"]:
				shap_data["plots"]["violin"] = violin_plot(shap_data["values"])
			st.pyplot(shap_data["plots"]["violin"], use_container_width=False)

			st.subheader(f"🌊 Waterfall Plot (instanța {instanta_xai})")
			if "waterfall" not in shap_data["plots"]:
				shap_data["plots"]["waterfall"] = waterfall_plot(shap_data["values"], instanta_xai)
			st.pyplot(shap_data["plots"]["waterfall"], use_container_width=False)

	elif tehnica_xai == "LIME":
		lime_data = st.session_state["xai"][denumire_model].setdefault("lime", {"explanation": None, "plot": None})

		if lime_data["explanation"] is None:
			with st.spinner("Generăm explicația LIME..."):
				lime_data["explanation"] = get_explanation(model, X_train, X_test, instanta_xai)

		if lime_data["explanation"] is not None:
			st.subheader(f"📈 Explicație locală pentru instanța {instanta_xai}")
			if lime_data["plot"] is None:
				lime_data["plot"] = explanation_plot(lime_data["explanation"])
			components.html(lime_data["plot"], height=600)

	elif tehnica_xai == "DiCE ML":
		st.session_state["xai"][denumire_model].setdefault("dice", {"explainer": None, "counterfactuals": {}})
		dice_data = st.session_state["xai"][denumire_model]["dice"]

		tinta = st.session_state.set_date["tinta"]
		date_instanta = X_test.iloc[[instanta_xai]]

		st.subheader("Exemplu selectat")
		st.write(date_instanta)

		try:
			if dice_data["explainer"] is None:
				with st.spinner("Creăm explainerul DiCE..."):
					dice_data["explainer"] = get_dice_explainer(model, X_train, y_train, tinta)

			counterfactuals = dice_data["counterfactuals"]

			if instanta_xai not in counterfactuals:
				with st.spinner("Generăm explicații contrafactuale..."):
					predictie, cf_df, diffs = calculate_counterfactuals(
						model, dice_data["explainer"], date_instanta, X_train.columns.tolist()
					)
					counterfactuals[instanta_xai] = {
						"predictie": predictie,
						"cf_df": cf_df,
						"diffs": diffs,
					}

			rezultate = counterfactuals[instanta_xai]
			predictie = rezultate["predictie"]
			cf_df = rezultate["cf_df"]
			diffs = rezultate["diffs"]

			st.subheader(f"🔮 Predicția modelului `{denumire_model}`: `{predictie}`")

			st.subheader("🍎 Modificări minime pentru a schimba predicția modelului:")
			st.dataframe(cf_df)

			st.subheader("🔍 Diferențe față de exemplul original")
			st.write(diffs.style.applymap(highlight_positive_negative))

		except Exception as e:
			st.error(f"Eroare la generarea explicațiilor pentru `{denumire_model}`: {e}")
