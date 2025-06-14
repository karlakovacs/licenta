import pandas as pd
import streamlit as st

from ml import predictie_individuala

from .descrieri import DESCRIERI_XAI
from .dice import (
	calculate_counterfactuals,
	get_dice_explainer,
)
from .lime import get_explanation, get_lime_explainer, lime_plot
from .shap import calculate_shap_values, get_shap_explainer, shap_plot


def ui_test(
	modele_antrenate: dict,
	X_train: pd.DataFrame,
	y_train: pd.Series,
	X_test: pd.DataFrame,
):
	st.session_state.setdefault("instante_test", {})
	denumire_model, tehnica_xai = ui_selectie_model_tehnica(modele_antrenate)
	instanta_idx = ui_selectie_instanta(X_test)
	X_explicat = X_test.iloc[[instanta_idx]]

	ui_xai(modele_antrenate, denumire_model, tehnica_xai, instanta_idx, X_train, y_train, X_explicat, False)


def ui_predictii(
	modele_antrenate: dict,
	X_train: pd.DataFrame,
	y_train: pd.Series,
	X_explicat: pd.DataFrame,
	instanta_idx: int,
):
	st.session_state.setdefault("instante_predictii", {})
	denumire_model, tehnica_xai = ui_selectie_model_tehnica(modele_antrenate, instanta_utilizator=True)

	ui_xai(
		modele_antrenate,
		denumire_model,
		tehnica_xai,
		instanta_idx,
		X_train,
		y_train,
		X_explicat,
		True,
	)


def ui_selectie_model_tehnica(modele_antrenate: dict, instanta_utilizator: bool = False):
	if not instanta_utilizator:
		st.session_state.setdefault("xai_test", {})
	else:
		st.session_state.setdefault("xai_predictii", {})

	cheie_predictie = "_predictie" if instanta_utilizator else ""
	col1, col2 = st.columns(2)
	with col1:
		optiuni_modele = list(modele_antrenate.keys())
		denumire_model = st.selectbox(
			"Alege modelul pentru care vrei să vezi analiza explicațiilor",
			optiuni_modele,
			key="model_xai" + cheie_predictie,
			help="Selectează modelul de machine learning asupra căruia vrei să aplici metodele XAI.",
		)

	with col2:
		tehnici_xai = ["SHAP", "LIME", "DiCE ML"]
		tehnica_xai = st.selectbox(
			"Alege tehnica de explicație (XAI)",
			tehnici_xai,
			key="tehnica_xai" + cheie_predictie,
			help="Selectează tehnica de explainable AI (XAI) pentru a interpreta deciziile modelului ales.",
		)

	return denumire_model, tehnica_xai


def ui_selectie_instanta(X_test):
	nr_instante = len(X_test)

	instanta_idx = st.slider(
		"Selectează exemplul de test pentru analiză",
		min_value=0,
		max_value=nr_instante - 1,
		value=0,
		key="instanta_xai",
		help="Alege indexul exemplului de test pentru care dorești să generezi explicații contrafactuale sau de importanță a caracteristicilor.",
	)

	return instanta_idx


def init_explainer(denumire_model: str, tehnica_xai: str, model, X_train: pd.DataFrame, y_train: pd.Series = None):
	if (
		"explainers" in st.session_state and
		denumire_model in st.session_state["explainers"] and
		tehnica_xai in st.session_state["explainers"][denumire_model]
	):
		del st.session_state["explainers"][denumire_model][tehnica_xai]

	if denumire_model in st.session_state.get("explainers", {}) and tehnica_xai in st.session_state["explainers"].get(
		denumire_model, {}
	):
		return st.session_state["explainers"][denumire_model][tehnica_xai]

	metadate = st.session_state.metadate_set_procesat

	if tehnica_xai == "SHAP":
		explainer = get_shap_explainer(model, X_train, denumire_model)
	elif tehnica_xai == "LIME":
		explainer = get_lime_explainer(model, X_train, metadate)
	elif tehnica_xai == "DiCE ML":
		explainer = get_dice_explainer(model, X_train, y_train, metadate)
	else:
		st.error(f"Tehnica XAI '{tehnica_xai}' nu este validă.")
		return None

	st.session_state.setdefault("explainers", {}).setdefault(denumire_model, {})
	st.session_state["explainers"][denumire_model][tehnica_xai] = explainer

	return explainer


def salvare_instanta(
	denumire_model: str,
	model,
	X_explicat: pd.DataFrame,
	instanta_idx: int,
	y_train: pd.Series = None,
	instanta_utilizator: bool = False,
):
	dictionar = "instante_predictii" if instanta_utilizator else "instante_test"
	st.session_state.setdefault(dictionar, {})

	if instanta_idx not in st.session_state[dictionar]:
		st.session_state[dictionar][instanta_idx] = {"date": X_explicat}
		if not instanta_utilizator and y_train is not None:
			st.session_state[dictionar][instanta_idx]["y_true"] = y_train.iloc[instanta_idx]

	if denumire_model not in st.session_state[dictionar][instanta_idx]:
		y_pred, y_prob = predictie_individuala(model, st.session_state[dictionar][instanta_idx]["date"])
		st.session_state[dictionar][instanta_idx][denumire_model] = {
			"y_pred": y_pred,
			"y_prob": round(y_prob * 100, 2),
		}


def afisare_instanta(
	denumire_model: str,
	instanta_idx: int,
	instanta_utilizator: bool = False,
):
	dictionar = "instante_predictii" if instanta_utilizator else "instante_test"
	instanta: dict = st.session_state[dictionar][instanta_idx]
	date = instanta["date"]
	y_true = instanta.get("y_true", None)
	y_pred = instanta[denumire_model]["y_pred"]
	y_prob = instanta[denumire_model]["y_prob"]

	st.header(f"Instanța {instanta_idx}")
	st.dataframe(date, use_container_width=True)

	cols = st.columns(3)
	with cols[0]:
		st.metric(label="**✅ Valoare reală**", value=y_true)
	with cols[1]:
		st.metric(label="**🔮 Predicția modelului**", value=y_pred)
	with cols[2]:
		st.metric(label="**🎲 Probabilitate True**", value=f"{y_prob}%")


def ui_xai(
	modele_antrenate: dict,
	denumire_model: str,
	tehnica_xai: str,
	instanta_idx: int,
	X_train: pd.DataFrame,
	y_train: pd.Series,
	X_explicat: pd.DataFrame,
	instanta_utilizator: bool = False,
):
	if not denumire_model or not tehnica_xai:
		return

	model = modele_antrenate[denumire_model]["model"]

	salvare_instanta(denumire_model, model, X_explicat, instanta_idx, y_train, instanta_utilizator)
	afisare_instanta(denumire_model, instanta_idx, instanta_utilizator)

	st.divider()

	st.header(f"Analiză {tehnica_xai} pentru modelul `{denumire_model}`", help=DESCRIERI_XAI[tehnica_xai])

	if tehnica_xai == "SHAP":
		ui_shap(
			denumire_model,
			model,
			X_train,
			X_explicat,
			instanta_idx,
			instanta_utilizator,
		)

	elif tehnica_xai == "LIME":
		ui_lime(
			denumire_model,
			model,
			X_train,
			X_explicat,
			instanta_idx,
			instanta_utilizator,
		)

	elif tehnica_xai == "DiCE ML":
		ui_dice(
			denumire_model,
			model,
			X_train,
			X_explicat,
			y_train,
			instanta_idx,
			instanta_utilizator,
		)


def ui_shap(
	denumire_model: str,
	model,
	X_train: pd.DataFrame,
	X_explicat: pd.DataFrame,
	instanta_idx: int,
	instanta_utilizator: bool,
	tehnica_xai: str = "SHAP",
):
	dictionar = "xai_predictii" if instanta_utilizator else "xai_test"
	date: dict = st.session_state.setdefault(dictionar, {}).setdefault(denumire_model, {}).setdefault(tehnica_xai, {})
	explainer = init_explainer(denumire_model, tehnica_xai, model, X_train)

	if instanta_idx not in date:
		with st.spinner("Generăm plotul SHAP..."):
			shap_values = calculate_shap_values(explainer, X_explicat)
			date[instanta_idx] = shap_plot(shap_values)

	if date.get(instanta_idx):
		st.pyplot(date[instanta_idx], use_container_width=False)
	else:
		st.info("Nu s-a putut genera graficul Waterfall Plot.")


def ui_lime(
	denumire_model: str,
	model,
	X_train: pd.DataFrame,
	X_explicat: pd.DataFrame,
	instanta_idx: int,
	instanta_utilizator: bool,
	tehnica_xai: str = "LIME",
):
	dictionar = "xai_predictii" if instanta_utilizator else "xai_test"
	date: dict = st.session_state.setdefault(dictionar, {}).setdefault(denumire_model, {}).setdefault(tehnica_xai, {})
	explainer = init_explainer(denumire_model, tehnica_xai, model, X_train)

	if instanta_idx not in date:
		with st.spinner("Generăm explicația LIME..."):
			explicatie = get_explanation(model, explainer, X_explicat)
			date[instanta_idx] = lime_plot(explicatie) if explicatie is not None else "Error"

	if date.get(instanta_idx) and date.get(instanta_idx) != "Error":
		st.plotly_chart(date[instanta_idx], use_container_width=False)
	else:
		st.info("Nu s-a putut genera explicația LIME.")


def ui_dice(
	denumire_model: str,
	model,
	X_train: pd.DataFrame,
	X_explicat: pd.DataFrame,
	y_train: pd.Series,
	instanta_idx: int,
	instanta_utilizator: bool,
	tehnica_xai: str = "DiCE ML",
):
	if denumire_model in [
		"Decision Tree",
		"Random Forest",
		"Balanced Random Forest",
		"AdaBoost",
		"XGBoost",
		"LightGBM",
	]:
		st.info(f"Analiza DiCE este indisponibilă pentru modelul `{denumire_model}`.")
		return

	dictionar = "xai_predictii" if instanta_utilizator else "xai_test"
	date: dict = st.session_state.setdefault(dictionar, {}).setdefault(denumire_model, {}).setdefault(tehnica_xai, {})
	explainer = init_explainer(denumire_model, tehnica_xai, model, X_train, y_train)

	if instanta_idx not in date:
		with st.spinner("Generăm explicații contrafactuale..."):
			metadate = st.session_state.metadate_set_procesat
			counterfactuals, explicatii, interpretari = calculate_counterfactuals(
				explainer, X_explicat, X_train.columns.tolist(), metadate
			)
			date[instanta_idx] = {
				"counterfactuals": counterfactuals,
				"explicatii": explicatii,
				"interpretari": interpretari,
			}

	counterfactuals = date[instanta_idx]["counterfactuals"]
	interpretari = date[instanta_idx]["interpretari"]

	if counterfactuals is not None and not counterfactuals.empty:
		st.subheader("Modificări minime pentru a schimba predicția modelului")
		st.dataframe(counterfactuals)

		st.subheader("Intepretări")
		st.write(interpretari)
	else:
		st.info("Nu s-au putut genera explicațiile DiCE ML (nu au fost gasite explicatii contrafactuale).")
