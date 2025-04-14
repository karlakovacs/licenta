import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


TIPURI_NUMERICE = [np.number]  # [float, int]
TIPURI_CATEGORIALE = ["object", "category", "bool"]


@st.cache_data
def get_coloane_categoriale(X: pd.DataFrame) -> list[str]:
	coloane: list[str] = list(X.select_dtypes(include=TIPURI_CATEGORIALE).columns)
	return coloane


def plot_pie_chart(serie: pd.Series, max_categorii: int = 25) -> go.Figure:
	categorie = "Categorie"
	numar_aparitii = "Număr de apariții"
	titlu = f"Distribuția valorilor pentru '{serie.name}'"

	if serie.nunique() > max_categorii:
		st.warning("Prea multe valori unice!")
		return
	else:
		data = serie.value_counts().reset_index()
		data.columns = [categorie, numar_aparitii]

		fig = go.Figure(
			data=[
				go.Pie(
					labels=data[categorie],
					values=data[numar_aparitii],
					textinfo="percent+label",
					hole=0.3,
				)
			]
		)

		fig.update_layout(title=titlu, height=500)

		return fig


def afisare_nunique(df: pd.DataFrame):
	coloane_categoriale = get_coloane_categoriale(df)
	if coloane_categoriale is None:
		st.warning("Nu există coloane categoriale în dataset.")
		return

	nunique_values = df[coloane_categoriale].nunique().reset_index()
	nunique_values.columns = ["Coloană", "Număr de valori unice"]

	st.subheader("Numărul de valori unice pentru variabilele categoriale")
	st.dataframe(nunique_values, use_container_width=False)
