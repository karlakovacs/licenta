import pandas as pd
import streamlit as st

from preprocessing import procesare_dataset
from utils import citire_date_predefinite, citire_date_temp, nav_bar


st.set_page_config(layout="wide", page_title="Procesare", page_icon="🛠️")
nav_bar()
st.title("Procesarea datelor")


denumire_dataset = st.session_state.get("denumire_dataset", None)
sursa = st.session_state.get("sursa_date", "predefinit")

df: pd.DataFrame = None

if sursa != "predefinit":
	df = citire_date_temp(denumire_dataset)
else:
	df = citire_date_predefinite(denumire_dataset)

if df is not None:
	st.header(denumire_dataset)
	st.dataframe(df.head())

	tinta = st.session_state.tinta

	st.header("Alegerea caracteristicilor semnificative")
	optiune_selectie = st.selectbox(
		"Alege metoda de selecție a caracteristicilor:",
		[
			"Informația mutuală",
			"Testul ANOVA",
			"Niciuna",
		],
	)

	nr_variabile = None
	if optiune_selectie in ["Testul Chi-Square", "Testul ANOVA"]:
		nr_variabile = st.slider(
			label="Alegeti nr de features",
			min_value=1,
			max_value=df.shape[1] - 1,
			value=df.shape[1] // 2,
			step=1,
		)

	st.header("Gestionarea dezechilibrului dintre clase")
	optiune_dezechilibru = st.selectbox(
		"Strategia de gestionare a dezechilibrului dintre clase:",
		["Undersampling", "Oversampling", "ADASYN", "Niciuna"],
	)

	st.header("Scalarea datelor")
	optiune_scalare = st.selectbox(
		"Alege metoda de scalare:", ["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"]
	)

	st.header("Împărțirea în seturile de antrenare și testare")
	dimensiune_test = st.slider(
		"Alege procentajul pentru setul de testare:",
		min_value=0.1,
		max_value=0.4,
		step=0.1,
		value=0.2,
	)
	stratificat = st.checkbox("Împărțire stratificată")

	if st.button("Preprocesare"):
		procesare_dataset(
			df,
			tinta,
			optiune_selectie,
			nr_variabile,
			optiune_dezechilibru,
			optiune_scalare,
			dimensiune_test,
			stratificat,
		)
else:
	st.warning("Alegeti un set de date")
