import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder
import streamlit as st


TIPURI_NUMERICE = [np.number]  # [float, int]
TIPURI_CATEGORIALE = ["object", "category", "bool"]


def afisare_descriere(df: pd.DataFrame):
	describe_numeric = df.describe(include=TIPURI_NUMERICE)
	describe_categorical = df.describe(include=TIPURI_CATEGORIALE)
	col1, col2 = st.columns(2)
	with col1:
		st.subheader("Variabile numerice")
		st.dataframe(describe_numeric)
	with col2:
		st.subheader("Variabile categoriale & booleene")
		st.dataframe(describe_categorical)


def plot_tipuri_variabile(X: pd.DataFrame):
	titlu = "Distribuția tipurilor de variabile"
	tip_coloana = "Tip de coloană"
	nr_variabile = "Număr de variabile"

	tipuri_variabile = X.dtypes.astype(str).value_counts().rename_axis(tip_coloana).reset_index(name=nr_variabile)
	tipuri_variabile[nr_variabile] = tipuri_variabile[nr_variabile].astype(int)
	st.write(tipuri_variabile)

	fig = go.Figure()

	fig.add_trace(
		go.Bar(
			x=tipuri_variabile[tip_coloana],
			y=tipuri_variabile[nr_variabile],
			text=tipuri_variabile[nr_variabile],
			marker=dict(
				color=tipuri_variabile[nr_variabile],
				colorscale="viridis",
			),
			hoverinfo="x+y",
		)
	)

	fig.update_layout(
		title=titlu,
		xaxis_title=tip_coloana,
		yaxis_title=nr_variabile,
		# template="plotly_white",
		height=500,
	)

	st.plotly_chart(fig, use_container_width=False)


def plot_matrice_corelatie(df: pd.DataFrame, coloane_selectate: list):
	if len(coloane_selectate) < 2:
		st.warning("Selectează cel puțin două coloane pentru a genera heatmap-ul.")
		return

	if df.dtypes.isin(TIPURI_CATEGORIALE).any():
		df = get_df_encoded(df)

	matrice_corelatie = df[coloane_selectate].corr().round(2)

	fig = go.Figure(
		data=go.Heatmap(
			z=matrice_corelatie.values,
			x=matrice_corelatie.columns.tolist(),
			y=matrice_corelatie.index.tolist(),
			colorscale="Viridis",
			zmin=-1,
			zmax=1,
			text=matrice_corelatie.values,
			texttemplate="%{text}",
			hoverinfo="text",
			showscale=True,
		)
	)

	fig.update_layout(
		title="Matricea de corelație",
		xaxis_title="Caracteristici",
		yaxis_title="Caracteristici",
		height=600,
		template="plotly_white",
	)

	st.plotly_chart(fig, use_container_width=False)


def get_df_encoded(X: pd.DataFrame):
	X_encoded = X.copy()
	for col in X_encoded.select_dtypes(include=TIPURI_CATEGORIALE).columns:
		le = LabelEncoder()
		X_encoded[col] = le.fit_transform(X_encoded[col])
	return X_encoded


@st.cache_data
def calcul_variabile_puternic_corelate(X: pd.DataFrame, y: pd.Series):
	variabila = "Variabilă"
	corelatie_absoluta = "Corelație absolută"
	X_encoded = get_df_encoded(X)
	corelatii_tinta = X_encoded.corrwith(y).abs().sort_values(ascending=False).reset_index()
	corelatii_tinta.columns = [variabila, corelatie_absoluta]
	return corelatii_tinta


def plot_variabile_puternic_corelate(X: pd.DataFrame, y: pd.Series):
	variabila = "Variabilă"
	corelatie_absoluta = "Corelație absolută"
	titlu = "Variabile puternic corelate cu ținta"

	corelatii_tinta = calcul_variabile_puternic_corelate(X, y)

	fig = go.Figure()

	fig.add_trace(
		go.Bar(
			x=corelatii_tinta[variabila],
			y=corelatii_tinta[corelatie_absoluta],
			marker=dict(
				color=corelatii_tinta[corelatie_absoluta],
				colorscale="viridis",
			),
			text=corelatii_tinta[corelatie_absoluta].round(2),
			textposition="outside",
		)
	)

	fig.update_layout(
		title=titlu,
		xaxis_title=variabila,
		yaxis_title=corelatie_absoluta,
		xaxis=dict(tickangle=-45),
		height=600,
	)

	st.plotly_chart(fig, use_container_width=False)


def plot_valori_lipsa(df: pd.DataFrame):
	variabila = "Variabilă"
	valori_lipsa = "Valori lipsă"
	procent = "Procent"
	titlu = "Procentul valorilor lipsă per coloană"
	missing_vals = df.isnull().sum()
	missing_percent = (missing_vals / len(df)) * 100

	missing_df = pd.DataFrame(
		{
			variabila: missing_vals.index,
			valori_lipsa: missing_vals.values,
			procent: missing_percent.values,
		}
	)
	missing_df = missing_df[missing_df[valori_lipsa] > 0].sort_values(procent, ascending=True)

	if missing_df.empty:
		st.success("Nu există valori lipsă în dataset!")
		return

	fig = go.Figure()
	fig.add_trace(
		go.Bar(
			y=missing_df[variabila],
			x=missing_df[procent],
			orientation="h",
			marker_color="orange",
		)
	)

	fig.update_layout(
		title=titlu,
		xaxis_title=procent,
		yaxis_title=variabila,
		bargap=0.2,
		margin=dict(l=100, r=20, t=50, b=50),
	)

	st.plotly_chart(fig, use_container_width=True)
