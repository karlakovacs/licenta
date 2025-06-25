import numpy as np
import pandas as pd
import streamlit as st

from dataset import *
from eda import *
from ui import *


initializare_pagina("EDA", "wide", "Analiza exploratorie a datelor", {"eda": {}})


def sectiune_set_date(df):
	interval = st.slider(
		"Selectează intervalul de rânduri de afișat",
		min_value=0,
		max_value=len(df) - 1,
		value=(0, min(200, len(df) - 1)),
		step=1,
		key="interval_observatii",
	)

	start, end = interval
	st.dataframe(df.iloc[start : end + 1], use_container_width=True)


def descriere_variabila(tip: str, serie: pd.Series):
	if tip.startswith("N"):
		rezultate = descriere_variabila_numerica(tip, serie)
	elif tip == "D":
		rezultate = descriere_variabila_data(tip, serie)
	elif tip == "T":
		rezultate = descriere_variabila_text(tip, serie)
	elif tip == "C" or tip == "B":
		rezultate = descriere_variabila_categoriala(tip, serie)
	else:
		rezultate = {"tip": tip, "statistici": {}}
	return rezultate


def afisare_descriere(variabila: str, descriere: dict):
	tip: str = descriere.get("tip", None)
	if tip.startswith("N"):
		afisare_descriere_variabila_numerica(variabila, descriere)
	elif tip == "D":
		afisare_descriere_variabila_data(variabila, descriere)
	elif tip == "T":
		afisare_descriere_variabila_text(variabila, descriere)
	elif tip == "C" or tip == "B":
		afisare_descriere_variabila_categoriala(variabila, descriere)
	else:
		st.warning("UFF")


def sectiune_descriere(df: pd.DataFrame):
	st.session_state["eda"].setdefault("descrieri", {})
	descrieri = st.session_state.eda["descrieri"]
	df = df.copy()
	variabila = st.selectbox("Alege o variabilă", df.columns)
	tip = get_tip_variabila(variabila)
	if variabila not in descrieri:
		with st.spinner("Calculam statistici..."):
			descrieri[variabila] = descriere_variabila(tip, df[variabila])

	afisare_descriere(variabila, descrieri[variabila])


def sectiune_tipuri_variabile(X):
	if "plot_tipuri_variabile" not in st.session_state.eda:
		st.session_state.eda["plot_tipuri_variabile"] = plot_tipuri_variabile(X)
	st.plotly_chart(st.session_state.eda["plot_tipuri_variabile"], use_container_width=False)


def sectiune_distributie_tinta(y: pd.Series):
	st.session_state.eda.setdefault("distributie_tinta", {})
	if "pie_chart_tinta" not in st.session_state.eda["distributie_tinta"]:
		st.session_state.eda["distributie_tinta"]["pie_chart_tinta"] = plot_pie_chart(y)
		st.session_state.eda["distributie_tinta"]["interpretare"] = interpretare_tinta(y)
	st.plotly_chart(st.session_state.eda["distributie_tinta"]["pie_chart_tinta"], use_container_width=False)
	st.write(st.session_state.eda["distributie_tinta"]["interpretare"])


def sectiune_matrice_corelatie(df: pd.DataFrame):
	coloane_selectate = st.multiselect(
		"Alege coloanele pentru matricea de corelație",
		df.select_dtypes(include=[np.number]).columns,
		help="Selectează variabile numerice pentru a construi o matrice de corelație.",
	)

	if coloane_selectate:
		st.session_state.eda["matrice_corelatie"] = plot_matrice_corelatie(df, coloane_selectate)
		st.plotly_chart(st.session_state.eda["matrice_corelatie"], use_container_width=True)
	else:
		st.info("Selectează cel puțin două coloane numerice pentru a genera graficul.")


def sectiune_valori_lipsa(df: pd.DataFrame):
	st.session_state.eda.setdefault("valori_lipsa", {})
	valori_lipsa = st.session_state.eda["valori_lipsa"]

	if "df" not in valori_lipsa:
		valori_lipsa["df"] = df_valori_lipsa(df)

	if valori_lipsa["df"] is not None and "fig" not in valori_lipsa:
		valori_lipsa["fig"] = plot_valori_lipsa(valori_lipsa["df"])

	if valori_lipsa["df"] is not None:
		st.dataframe(valori_lipsa["df"], use_container_width=False)
		st.plotly_chart(valori_lipsa["fig"], use_container_width=False)
	else:
		st.success("Nu există valori lipsă în dataset!")


def sectiune_corelatie_tinta(X, y):
	if "plot_variabile_puternic_corelate" not in st.session_state.eda:
		st.session_state.eda["plot_variabile_puternic_corelate"] = plot_variabile_puternic_corelate(X, y)
	st.plotly_chart(st.session_state.eda["plot_variabile_puternic_corelate"], use_container_width=False)


@require_auth
@require_selected_dataset
def main():
	set_date: dict = st.session_state.get("set_date", None)
	df: pd.DataFrame = citire_set_date(set_date)

	tinta = set_date["tinta"]
	X = df.drop(columns=[tinta]).copy()
	y = df[tinta]

	functii = {
		"Setul de date": lambda: sectiune_set_date(df),
		"Analiza valorilor lipsă": lambda: sectiune_valori_lipsa(df),
		"Distribuția tipurilor de variabile": lambda: sectiune_tipuri_variabile(X),
		"Distribuția variabilei țintă": lambda: sectiune_distributie_tinta(y),
		"Statistici descriptive": lambda: sectiune_descriere(X),
		"Matricea de corelație": lambda: sectiune_matrice_corelatie(df),
		"Variabilele puternic corelate cu ținta": lambda: sectiune_corelatie_tinta(X, y),
	}

	detalii = {
		"Setul de date": "Afișează setul de date în mod interactiv.\n\nPermite o primă verificare a consistenței datelor.\n\nUtil pentru a înțelege structura brută a fișierului încărcat.",
		"Analiza valorilor lipsă": "Evaluează câte valori lipsesc pe coloană, atât în număr absolut, cât și procentual.\n\nEste utilă pentru luarea deciziilor de curățare a datelor sau imputare.",
		"Distribuția tipurilor de variabile": "Arată câte variabile sunt de tip numeric, categoric, boolean, text sau dată.\n\nAceastă informație este crucială pentru alegerea corectă a metodelor de preprocesare și analiză.",
		"Distribuția variabilei țintă": "Afișează distribuția clasei țintă (`target`), importantă pentru detectarea dezechilibrelor între clase.\n\nUn dezechilibru sever poate afecta performanța modelelor de clasificare.",
		"Statistici descriptive": "Oferă statistici relevante pentru fiecare variabilă, în funcție de tipul ei: medii, extreme, dispersie, modă, distribuție etc.\n\nAjută la înțelegerea comportamentului fiecărei variabile în mod individual.",
		"Matricea de corelație": "Prezintă corelațiile între variabile numerice. Coeficientul Pearson este folosit pentru a detecta relații liniare.\n\nPoate evidenția redundanțe sau relații utile pentru modelare.",
		"Variabilele puternic corelate cu ținta": "Identifică variabilele numerice care au o corelație puternică (pozitivă sau negativă) cu variabila țintă.\n\nAcestea pot fi predictori relevanți în modelele de clasificare.",
	}

	selectie = None

	col1, col2 = st.columns([1, 3])

	with col1:
		selectie = st.selectbox("Ce vrei să vizualizezi?", functii.keys())
		with st.expander("Informații despre analiza curentă"):
			st.write(detalii[selectie])

	with col2:
		functii[selectie]()


if __name__ == "__main__":
	main()
