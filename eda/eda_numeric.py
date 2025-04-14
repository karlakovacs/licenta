import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


TIPURI_NUMERICE = [np.number]  # [float, int]


@st.cache_data
def get_coloane_numerice(df: pd.DataFrame) -> list[str]:
	coloane: list[str] = list(df.select_dtypes(include=TIPURI_NUMERICE).columns)
	return coloane


def get_df_numeric(df: pd.DataFrame):
	coloane = get_coloane_numerice(df)
	return df[coloane] if coloane is not None else None


def plot_histograma(serie: pd.Series, nr_bins: int = 30) -> go.Figure:
	nume_variabila = serie.name
	frecventa = "Frecvență"
	titlu = f"Histogramă pentru '{nume_variabila}'"
	fig = go.Figure(data=[go.Histogram(x=serie, nbinsx=nr_bins)])

	fig.update_layout(
		title=titlu,
		xaxis_title=nume_variabila,
		yaxis_title=frecventa,
		bargap=0.1,  # to try
		template="plotly_white",
	)

	return fig


def afisare_outliers_data(df: pd.DataFrame):
	df_numeric = get_df_numeric(df)
	variabile = df_numeric.columns
	summary_data = []

	for col in variabile:
		Q1 = df[col].quantile(0.25)
		Q3 = df[col].quantile(0.75)
		IQR = Q3 - Q1
		lower_bound = Q1 - 1.5 * IQR
		upper_bound = Q3 + 1.5 * IQR
		num_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
		percent_outliers = (num_outliers / len(df)) * 100

		summary_data.append(
			{
				"Coloană": col,
				"Limita inferioară": lower_bound,
				"Limita superioară": upper_bound,
				"Număr outlieri": num_outliers,
				"Procent outlieri (%)": percent_outliers,
			}
		)
	df_outlier_data = pd.DataFrame(summary_data)
	st.dataframe(df_outlier_data)


def plot_box_plot(serie: pd.Series) -> go.Figure:
	nume_variabila = serie.name
	titlu = f"Box plot pentru '{nume_variabila}'"
	fig = go.Figure()
	fig.add_trace(
		go.Box(
			y=serie,
			name=nume_variabila,
			boxmean=True,
			marker=dict(color="royalblue"),
		)
	)
	fig.update_layout(title=titlu, yaxis_title=nume_variabila)
	return fig
