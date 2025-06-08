import pandas as pd
import streamlit as st

from .descrieri import DESCRIERI_XAI
from .dice import (
	calculate_counterfactuals,
	get_dice_explainer,
	interpretare_explicatii,
)
from .lime import explanation_plotly, get_explanation
from .shap import bar_plot, calculate_shap_values, violin_plot, waterfall_plot


def ui_date_test(
	modele_antrenate: dict,
	X_train: pd.DataFrame,
	X_test: pd.DataFrame,
	y_train: pd.Series,
):
	denumire_model, tehnica_xai = ui_selectie_model_tehnica(modele_antrenate)
	instanta_idx = ui_selectie_instanta(denumire_model, X_test)
	ui_xai(
		modele_antrenate,
		denumire_model=denumire_model,
		tehnica_xai=tehnica_xai,
		instanta_idx=instanta_idx,
		X_train=X_train,
		X_test=X_test,
		y_train=y_train,
	)


def ui_predictii(
	modele_antrenate: dict,
	X_train: pd.DataFrame,
	y_train: pd.Series,
	instanta: pd.DataFrame,
	counter_idx: int,
):
	denumire_model, tehnica_xai = ui_selectie_model_tehnica(modele_antrenate, predictie_individuala=True)
	ui_xai(
		modele_antrenate,
		denumire_model=denumire_model,
		tehnica_xai=tehnica_xai,
		instanta_idx=counter_idx,
		predictie_individuala=True,
		X_train=X_train,
		y_train=y_train,
		instanta=instanta,
	)


def ui_selectie_model_tehnica(modele_antrenate: dict, predictie_individuala: bool = False):
	if not predictie_individuala:
		st.session_state.setdefault("xai", {})
	else:
		st.session_state.setdefault("xai_predictii", {})

	optiuni_modele = list(modele_antrenate.keys())

	cheie_predictie = "_predictie" if predictie_individuala else ""

	denumire_model = st.selectbox(
		"Alege modelul pentru care vrei să vezi analiza explicațiilor",
		optiuni_modele,
		key="model_xai" + cheie_predictie,
		help="Selectează modelul de machine learning asupra căruia vrei să aplici metodele XAI.",
	)

	tehnici_xai = ["SHAP", "LIME", "DiCE ML"]
	tehnica_xai = st.selectbox(
		"Alege tehnica de explicație (XAI)",
		tehnici_xai,
		key="tehnica_xai" + cheie_predictie,
		help="Selectează tehnica de explainable AI (XAI) pentru a interpreta deciziile modelului ales.",
	)

	return denumire_model, tehnica_xai


def ui_selectie_instanta(denumire_model, X_test):
	nr_instante = (
		len(X_test)
		if denumire_model
		not in ["Quadratic Discriminant Analysis", "K-Nearest Neighbors", "Support Vector Classifier", "AdaBoost"]
		else 50
	)

	instanta_idx = st.slider(
		"Selectează exemplul de test pentru analiză",
		min_value=0,
		max_value=nr_instante - 1,
		value=0,
		key="instanta_xai",
		help="Alege indexul exemplului de test pentru care dorești să generezi explicații contrafactuale sau de importanță a caracteristicilor.",
	)

	return instanta_idx


def ui_xai(
	modele_antrenate: dict,
	denumire_model: str,
	tehnica_xai: str,
	instanta_idx: int,
	predictie_individuala: bool = False,
	X_train: pd.DataFrame = None,
	X_test: pd.DataFrame = None,
	y_train: pd.Series = None,
	instanta: pd.DataFrame = None,
):
	if not denumire_model or not tehnica_xai:
		return

	st.header(f"Analiză {tehnica_xai} pentru modelul `{denumire_model}`")
	model = modele_antrenate[denumire_model]["model"]

	if tehnica_xai == "SHAP":
		if predictie_individuala:
			ui_shap_predictie_noua(
				denumire_model=denumire_model,
				model=model,
				X_train=X_train,
				instanta=instanta,
				instanta_idx=instanta_idx,
			)
		else:
			ui_shap_set_testare(
				denumire_model=denumire_model,
				model=model,
				X_train=X_train,
				X_test=X_test,
				instanta_xai=instanta_idx,
			)

	elif tehnica_xai == "LIME":
		ui_lime(
			denumire_model=denumire_model,
			model=model,
			X_train=X_train,
			instanta=instanta if predictie_individuala else X_test,
			instanta_idx=instanta_idx,
			predictie_individuala=predictie_individuala,
		)

	elif tehnica_xai == "DiCE ML":
		ui_dice(
			denumire_model=denumire_model,
			model=model,
			X_train=X_train,
			instanta=instanta if predictie_individuala else X_test.iloc[[instanta_idx]],
			y_train=y_train,
			instanta_idx=instanta_idx,
			predictie_individuala=predictie_individuala,
		)


def ui_shap_set_testare(denumire_model, model, X_train, X_test, instanta_xai=0):
	if denumire_model in ["Decision Tree", "Random Forest", "Balanced Random Forest", "AdaBoost"]:
		st.info(f"Analiza SHAP este indisponibilă pentru modelul `{denumire_model}`.")
		return

	shap_data = st.session_state["xai"].setdefault(denumire_model, {}).setdefault("shap", {"values": None, "plots": {}})

	if shap_data["values"] is None:
		with st.spinner("Calculăm valorile SHAP..."):
			shap_data["values"] = calculate_shap_values(model, X_train, X_test)

	if shap_data["values"] == "Error":
		st.info("Nu s-au putut calcula valorile SHAP.")
		return

	st.subheader("📊 Bar Plot")
	if "bar" not in shap_data["plots"]:
		shap_data["plots"]["bar"] = bar_plot(shap_data["values"])
	if shap_data["plots"]["bar"]:
		st.pyplot(shap_data["plots"]["bar"], use_container_width=False)
		with st.popover("Detalii despre SHAP Bar Plot"):
			st.write(DESCRIERI_XAI["bar"])
	else:
		st.info("Nu s-a putut genera graficul Bar Plot.")

	st.subheader("🎻 Violin Plot")
	if "violin" not in shap_data["plots"]:
		shap_data["plots"]["violin"] = violin_plot(shap_data["values"])
	if shap_data["plots"]["violin"]:
		st.pyplot(shap_data["plots"]["violin"], use_container_width=False)
		with st.popover("Detalii despre SHAP Violin Plot"):
			st.write(DESCRIERI_XAI["violin"])
	else:
		st.info("Nu s-a putut genera graficul Violin Plot.")

	st.subheader(f"🌊 Waterfall Plot (instanța {instanta_xai})")
	if "waterfall" not in shap_data["plots"]:
		shap_data["plots"]["waterfall"] = {}
	if instanta_xai not in shap_data["plots"]["waterfall"]:
		shap_data["plots"]["waterfall"][instanta_xai] = waterfall_plot(shap_data["values"], instanta_xai)
	if shap_data["plots"]["waterfall"][instanta_xai]:
		st.pyplot(shap_data["plots"]["waterfall"][instanta_xai], use_container_width=False)
		with st.popover("Detalii despre SHAP Waterfall Plot"):
			st.write(DESCRIERI_XAI["waterfall"])
	else:
		st.info("Nu s-a putut genera graficul Waterfall Plot.")


def ui_shap_predictie_noua(denumire_model, model, X_train, instanta: pd.DataFrame, instanta_idx: int):
	if denumire_model in ["Decision Tree", "Random Forest", "Balanced Random Forest", "AdaBoost"]:
		st.info(f"Analiza SHAP este indisponibilă pentru modelul `{denumire_model}`.")
		return

	# del st.session_state["xai_predictii"]

	shap_data = (
		st.session_state["xai_predictii"].setdefault(denumire_model, {}).setdefault("shap", {"values": {}, "plots": {}})
	)

	with st.spinner("Calculăm SHAP pentru instanța nouă..."):
		shap_data["values"][instanta_idx] = calculate_shap_values(model, X_train, instanta)

	if shap_data["values"][instanta_idx] == "Error":
		st.info("Nu s-au putut calcula valorile SHAP.")
		return

	st.subheader(f"🌊 Waterfall Plot (instanța nouă)")
	if "waterfall" not in shap_data["plots"]:
		shap_data["plots"]["waterfall"] = {}
	shap_data["plots"]["waterfall"][instanta_idx] = waterfall_plot(shap_data["values"][instanta_idx], instanta_idx)
	if shap_data["plots"]["waterfall"][instanta_idx]:
		st.pyplot(shap_data["plots"]["waterfall"][instanta_idx], use_container_width=False)
		with st.popover("Detalii despre SHAP Waterfall Plot"):
			st.write(DESCRIERI_XAI["waterfall"])
	else:
		st.info("Nu s-a putut genera graficul Waterfall Plot.")


def ui_lime(
	denumire_model: str,
	model,
	X_train: pd.DataFrame,
	instanta: pd.DataFrame,
	instanta_idx: int,
	predictie_individuala: bool = False,
):
	sesiune = "xai_predictii" if predictie_individuala else "xai"
	lime_data = (
		st.session_state.setdefault(sesiune, {}).setdefault(denumire_model, {}).setdefault("lime", {"explanations": {}})
	)

	if instanta_idx not in lime_data["explanations"]:
		with st.spinner("Generăm explicația LIME..."):
			index_explicatie = 0 if predictie_individuala else instanta_idx
			lime_data["explanations"][instanta_idx] = get_explanation(model, X_train, instanta, index_explicatie)

	sub = (
		f"📈 Explicație locală pentru instanța nouă ({instanta_idx})"
		if predictie_individuala
		else f"📈 Explicație locală pentru instanța {instanta_idx}"
	)
	st.subheader(sub)

	explicatie = lime_data["explanations"][instanta_idx]
	if explicatie is not None:
		st.plotly_chart(explanation_plotly(explicatie), use_container_width=False)
		with st.popover("Detalii despre LIME Plot"):
			st.write(DESCRIERI_XAI["lime"])
	else:
		st.info("Nu s-a putut genera explicația LIME.")


def ui_dice(
	denumire_model: str,
	model,
	X_train: pd.DataFrame,
	instanta: pd.DataFrame,
	y_train: pd.Series,
	instanta_idx: int,
	predictie_individuala: bool = False,
):
	sesiune = "xai_predictii" if predictie_individuala else "xai"
	del st.session_state[sesiune]

	st.session_state.setdefault(sesiune, {})
	st.session_state[sesiune].setdefault(denumire_model, {}).setdefault(
		"dice", {"explainer": None, "counterfactuals": {}}
	)
	dice_data = st.session_state[sesiune][denumire_model]["dice"]

	st.subheader("Instanța selectată" if not predictie_individuala else "Instanța introdusă")
	st.write(instanta)

	tinta = st.session_state.set_date["tinta"]

	if dice_data["explainer"] is None:
		with st.spinner("Creăm explainerul DiCE..."):
			dice_data["explainer"] = get_dice_explainer(model, X_train, y_train, tinta)

	if instanta_idx not in dice_data["counterfactuals"]:
		with st.spinner("Generăm explicații contrafactuale..."):
			predictie, cf_df, explicatii = calculate_counterfactuals(
				model, dice_data["explainer"], instanta, X_train.columns.tolist()
			)
			dice_data["counterfactuals"][instanta_idx] = {
				"predictie": predictie,
				"cf_df": cf_df,
				"explicatii": explicatii,
			}

	afisare_rezultate_dice(dice_data["counterfactuals"][instanta_idx], denumire_model)


def afisare_rezultate_dice(rezultate: dict, denumire_model: str):
	predictie, cf_df, explicatii = rezultate.values()

	if not any(rezultate.get(k) is None for k in ["predictie", "cf_df", "explicatii"]):
		st.subheader(f"🔮 Predicția modelului `{denumire_model}`: `{predictie}`")

		st.subheader("🍎 Modificări minime pentru a schimba predicția modelului")
		st.dataframe(cf_df)

		st.subheader("🔍 Intepretări")
		st.write(interpretare_explicatii(explicatii))

		with st.popover("Detalii despre DiCE ML"):
			st.write(DESCRIERI_XAI["dice"])
	else:
		st.info("Nu s-au putut genera explicațiile DiCE ML.")
