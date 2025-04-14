import pandas as pd
import streamlit as st

from eda import (
	descriere_variabile,
	df_valori_lipsa,
	get_coloane_categoriale,
	get_coloane_numerice,
	plot_box_plot,
	plot_histograma,
	plot_matrice_corelatie,
	plot_pie_chart,
	plot_tipuri_variabile,
	plot_valori_lipsa,
	plot_variabile_puternic_corelate,
)
from utils import citire_date_predefinite, citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="EDA", page_icon="📊")
st.title("Analiza exploratorie a datelor")
nav_bar()

set_date: dict = st.session_state.get("set_date", None)
st.session_state.setdefault("eda", {})

df: pd.DataFrame = None

if set_date["sursa"] != "predefinit":
	df = citire_date_temp(set_date["denumire"])
else:
	df = citire_date_predefinite(set_date["denumire"])


# taburi
def tab_descriere(df):
	if "describe_numeric" not in st.session_state.eda or "describe_categorical" not in st.session_state.eda:
		describe_numeric, describe_categorical = descriere_variabile(df)
		st.session_state.eda["describe_numeric"] = describe_numeric
		st.session_state.eda["describe_categorical"] = describe_categorical

	col1, col2 = st.columns(2)

	with col1:
		st.subheader("Variabile numerice")
		st.dataframe(st.session_state.eda["describe_numeric"])

	with col2:
		st.subheader("Variabile categoriale & booleene")
		st.dataframe(st.session_state.eda["describe_categorical"])


def tab_tipuri_variabile(X):
	if "plot_tipuri_variabile" not in st.session_state.eda:
		st.session_state.eda["plot_tipuri_variabile"] = plot_tipuri_variabile(X)
	st.plotly_chart(st.session_state.eda["plot_tipuri_variabile"], use_container_width=False)


def tab_distributie_tinta(y):
	if "pie_chart_tinta" not in st.session_state.eda:
		st.session_state.eda["pie_chart_tinta"] = plot_pie_chart(y)
	st.plotly_chart(st.session_state.eda["pie_chart_tinta"], use_container_width=False)


def tab_pie_charts(X: pd.DataFrame):
	coloane_categoriale = get_coloane_categoriale(X)
	if coloane_categoriale:
		st.session_state.eda.setdefault("pie_charts", {})
		coloane_selectate = st.multiselect("Alege coloanele pentru pie chart", coloane_categoriale)
		for col in coloane_selectate:
			if col not in st.session_state.eda["pie_charts"]:
				st.session_state.eda["pie_charts"][col] = plot_pie_chart(X[col])

		for col, fig in st.session_state.eda["pie_charts"].items():
			st.subheader(f"Distribuția variabilei {col}")
			st.plotly_chart(fig, use_container_width=False)
	else:
		st.warning("Nu exista coloane categoriale in setul de date.")


def tab_histograme(X):
	coloane_numerice = get_coloane_numerice(X)
	if coloane_numerice:
		st.session_state.eda.setdefault("histograme", {})
		nr_bins = st.slider("Alege numărul de bins:", min_value=5, max_value=50, value=20)
		coloane_selectate = st.multiselect("Alege coloanele pentru histogramă", coloane_numerice)
		for col in coloane_selectate:
			if col not in st.session_state.eda["histograme"]:
				st.session_state.eda["histograme"][col] = plot_histograma(X[col], nr_bins)

		for col, fig in st.session_state.eda["histograme"].items():
			st.subheader(f"Distribuția variabilei {col}")
			st.plotly_chart(fig, use_container_width=False)
	else:
		st.warning("Nu exista coloane numerice in setul de date.")


def tab_box_plots(X):
	coloane_numerice = get_coloane_numerice(X)
	if coloane_numerice:
		st.session_state.eda.setdefault("box_plots", {})
		coloane_selectate = st.multiselect("Alege coloanele pentru box plot", coloane_numerice)
		for col in coloane_selectate:
			if col not in st.session_state.eda["box_plots"]:
				st.session_state.eda["box_plots"][col] = plot_box_plot(X[col])

		for col, fig in st.session_state.eda["box_plots"].items():
			st.subheader(f"Box plot pentru variabila {col}")
			st.plotly_chart(fig, use_container_width=False)
	else:
		st.warning("Nu exista coloane numerice in setul de date.")


def tab_matrice_corelatie(df):
	st.session_state.eda.setdefault("plot_matrice_corelatie", {"coloane": [], "fig": None})
	coloane_selectate = st.multiselect(
		"Alege coloanele pentru matricea de corelație",
		df.columns,
		default=st.session_state.eda["plot_matrice_corelatie"]["coloane"],
	)

	if set(coloane_selectate) != set(st.session_state.eda["plot_matrice_corelatie"]["coloane"]):
		st.session_state.eda["plot_matrice_corelatie"]["fig"] = plot_matrice_corelatie(df, coloane_selectate)
		st.session_state.eda["plot_matrice_corelatie"]["coloane"] = coloane_selectate

	if st.session_state.eda["plot_matrice_corelatie"]["fig"] is not None:
		st.plotly_chart(st.session_state.eda["plot_matrice_corelatie"]["fig"], use_container_width=True)


def tab_valori_lipsa(df: pd.DataFrame):
	st.session_state.eda.setdefault("valori_lipsa", {})
	valori_lipsa = st.session_state.eda["valori_lipsa"]

	if "df" not in valori_lipsa:
		valori_lipsa["df"] = df_valori_lipsa(df)

	st.dataframe(valori_lipsa["df"], use_container_width=False)

	nr_variabile = st.slider("Alege numărul de variabile:", min_value=5, max_value=50, value=10)
	prev_nr = valori_lipsa.get("nr_variabile", None)

	if valori_lipsa["df"] is not None:
		if "fig" not in valori_lipsa or nr_variabile != prev_nr:
			valori_lipsa["fig"] = plot_valori_lipsa(valori_lipsa["df"], nr_variabile)
			valori_lipsa["nr_variabile"] = nr_variabile

		st.plotly_chart(valori_lipsa["fig"], use_container_width=False)


def tab_corelatie_tinta(X, y):
	if "plot_variabile_puternic_corelate" not in st.session_state.eda:
		st.session_state.eda["plot_variabile_puternic_corelate"] = plot_variabile_puternic_corelate(X, y)
	st.plotly_chart(st.session_state.eda["plot_variabile_puternic_corelate"], use_container_width=False)


# dictionar taburi
TAB_FUNCTII = {
	# "Descrierea setului de date": lambda: tab_descriere(df),
	"Valori lipsa": lambda: tab_valori_lipsa(df),
	"Distribuția tipurilor de variabile": lambda: tab_tipuri_variabile(X),
	"Distribuția variabilei țintă": lambda: tab_distributie_tinta(y),
	# "Pie charts (pentru variabilele categoriale)": lambda: tab_pie_charts(X),
	# "Histograme (pentru variabilele numerice)": lambda: tab_histograme(X),
	# "Box plots (pentru variabilele numerice)": lambda: tab_box_plots(X),
	# "Matricea de corelație": lambda: tab_matrice_corelatie(df),
	# "Variabile puternic corelate cu ținta": lambda: tab_corelatie_tinta(X, y),
}

if df is not None:
	tinta = set_date["tinta"]
	X = df.drop(columns=[tinta]).copy()
	y = df[tinta]

	tabs = st.tabs(TAB_FUNCTII.keys())
	for tab, (titlu, functie) in zip(tabs, TAB_FUNCTII.items()):
		with tab:
			st.subheader(titlu)
			functie()
else:
	st.warning(f"Datele pentru {set_date['denumire']} nu au fost încărcate corect sau lipsesc!")
