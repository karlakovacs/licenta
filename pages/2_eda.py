import pandas as pd
import streamlit as st

from eda import (
	afisare_descriere,
	get_coloane_numerice,
	plot_histograma,
	plot_matrice_corelatie,
	plot_pie_chart,
	plot_tipuri_variabile,
	plot_variabile_puternic_corelate,
)
from utils import citire_date_predefinite, citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="EDA", page_icon="📊")
st.title("Exploratory Data Analysis")
nav_bar()

# incarcare date
nume_dataset = st.session_state.get("nume_dataset", None)
sursa = st.session_state.get("sursa_date", "predefinit")
st.header(nume_dataset)

df: pd.DataFrame = None

if sursa != "predefinit":
	df = citire_date_temp(nume_dataset)
else:
	df = citire_date_predefinite(nume_dataset)


# taburi
def tab_descriere(df):
	afisare_descriere(df)


def tab_tipuri_variabile(X):
	plot_tipuri_variabile(X)


def tab_distributie_tinta(y):
	plot_pie_chart(y)


def tab_histograme(X):
	coloane_numerice = get_coloane_numerice(X)
	coloane_selectate = st.multiselect("Alege coloanele pentru histogramă", coloane_numerice)
	nr_bins = st.slider("Alege numărul de bins:", min_value=5, max_value=50, value=20)
	for col in coloane_selectate:
		plot_histograma(X, col, nr_bins)


def tab_box_plots(X):
	coloane_numerice = get_coloane_numerice(X)
	coloane_selectate = st.multiselect("Alege coloanele pentru box plot", coloane_numerice)
	# TODO: Adaugă funcția plot_box(coloane_selectate)


def tab_matrice_corelatie(df):
	coloane_selectate = st.multiselect(
		"Alege coloanele pentru matricea de corelație",
		df.columns,
		default=[df.columns[0], df.columns[-1]],
	)
	plot_matrice_corelatie(df, coloane_selectate)


def tab_corelatie_tinta(X, y):
	plot_variabile_puternic_corelate(X, y)


# dictionar taburi
TAB_FUNCTII = {
	"Descrierea setului de date": lambda: tab_descriere(df),
	"Distribuția tipurilor de variabile": lambda: tab_tipuri_variabile(X),
	"Distribuția variabilei țintă": lambda: tab_distributie_tinta(y),
	"Histograme (pentru variabilele numerice)": lambda: tab_histograme(X),
	"Box plots (pentru variabilele numerice)": lambda: tab_box_plots(X),
	"Matricea de corelație": lambda: tab_matrice_corelatie(df),
	"Variabile puternic corelate cu ținta": lambda: tab_corelatie_tinta(X, y),
}

# main
if df is not None:
	tinta = st.session_state.get("tinta")
	X = df.drop(columns=[tinta]).copy()
	y = df[tinta]

	tabs = st.tabs(TAB_FUNCTII.keys())
	for tab, (titlu, functie) in zip(tabs, TAB_FUNCTII.items()):
		with tab:
			st.subheader(titlu)
			functie()
else:
	st.warning(f"Datele pentru {nume_dataset} nu au fost încărcate corect sau lipsesc!")
