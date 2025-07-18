import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
from sklearn.preprocessing import LabelEncoder
import streamlit as st

from .color_decorator import with_random_color


TIPURI_NUMERICE = [np.number]  # [float, int]
TIPURI_CATEGORIALE = ["object", "category", "bool"]


@with_random_color
def plot_tipuri_variabile(X: pd.DataFrame, culoare: str = None) -> go.Figure:
	titlu = "Distribuția tipurilor de variabile"
	tip_coloana = "Tip de coloană"
	nr_variabile = "Număr de variabile"

	tipuri_variabile = X.dtypes.astype(str).value_counts().rename_axis(tip_coloana).reset_index(name=nr_variabile)
	tipuri_variabile[nr_variabile] = tipuri_variabile[nr_variabile].astype(int)

	fig = go.Figure()

	fig.add_trace(
		go.Bar(
			x=tipuri_variabile[tip_coloana],
			y=tipuri_variabile[nr_variabile],
			text=tipuri_variabile[nr_variabile],
			marker=dict(color=culoare),
			hoverinfo="x+y",
		)
	)

	fig.update_layout(
		title=titlu,
		xaxis_title=tip_coloana,
		yaxis_title=nr_variabile,
		height=500,
	)

	return fig


def plot_matrice_corelatie(df: pd.DataFrame, coloane_selectate: list) -> go.Figure:
	if len(coloane_selectate) < 2:
		st.warning("Selectează cel puțin două coloane pentru a genera heatmap-ul.")
		return None

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
		yaxis_autorange="reversed",
		height=600,
		template="plotly_white",
	)

	return fig


def get_df_encoded(X: pd.DataFrame):
	X_encoded = X.copy()
	for col in X_encoded.select_dtypes(include=TIPURI_CATEGORIALE).columns:
		le = LabelEncoder()
		X_encoded[col] = le.fit_transform(X_encoded[col])
	return X_encoded


# def calcul_variabile_puternic_corelate(X: pd.DataFrame, y: pd.Series):
# 	variabila = "Variabilă"
# 	corelatie_absoluta = "Corelație absolută"
# 	X_encoded = get_df_encoded(X)
# 	if not pd.api.types.is_numeric_dtype(y):
# 		y = y.astype("category")
# 	corelatii_tinta = X_encoded.corrwith(y).abs().sort_values(ascending=False).reset_index()
# 	corelatii_tinta.columns = [variabila, corelatie_absoluta]
# 	return corelatii_tinta


def cramers_v(x, y):
	confusion_matrix = pd.crosstab(x, y)
	chi2, _, _, _ = chi2_contingency(confusion_matrix)
	n = confusion_matrix.sum().sum()
	phi2 = chi2 / n
	r, k = confusion_matrix.shape
	phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
	rcorr = r - ((r - 1) ** 2) / (n - 1)
	kcorr = k - ((k - 1) ** 2) / (n - 1)
	return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))


def calculeaza_corelatie(x: pd.Series, y: pd.Series) -> float:
	try:
		if pd.api.types.is_numeric_dtype(x):
			return abs(x.corr(y))
		else:
			return cramers_v(x.astype(str), y)
	except Exception:
		return np.nan

def calcul_variabile_puternic_corelate(X: pd.DataFrame, y: pd.Series, max_categorii: int = 100) -> pd.DataFrame:
	variabila = "Variabilă"
	corelatie_absoluta = "Corelație absolută"

	if not pd.api.types.is_numeric_dtype(y):
		y = pd.factorize(y)[0]

	rezultate = []

	for col in X.columns:
		x = X[col]

		if pd.api.types.is_datetime64_any_dtype(x):
			continue

		if x.isnull().all():
			continue

		if x.nunique(dropna=True) <= 1:
			continue

		if (not pd.api.types.is_numeric_dtype(x)) and x.nunique(dropna=True) > max_categorii:
			continue

		valid_idx = x.notna() & pd.Series(y).notna()
		x_valid = x[valid_idx]
		y_valid = pd.Series(y)[valid_idx]

		coef = calculeaza_corelatie(x_valid, y_valid)
		rezultate.append({variabila: col, corelatie_absoluta: coef})

	df_rezultat = pd.DataFrame(rezultate).sort_values(corelatie_absoluta, ascending=False).reset_index(drop=True)
	return df_rezultat


def plot_variabile_puternic_corelate(X: pd.DataFrame, y: pd.Series) -> go.Figure:
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

	return fig


def df_valori_lipsa(df: pd.DataFrame) -> pd.DataFrame:
	variabila = "Variabilă"
	valori_lipsa = "Valori lipsă"
	procent = "Procent"
	missing_vals = df.isnull().sum()
	missing_percent = (missing_vals / len(df)) * 100

	missing_df = pd.DataFrame(
		{
			variabila: missing_vals.index,
			valori_lipsa: missing_vals.values,
			procent: missing_percent.values,
		}
	)
	missing_df = missing_df[missing_df[valori_lipsa] > 0].sort_values(procent, ascending=False).reset_index()
	missing_df.drop(columns=["index"], inplace=True)

	if missing_df.empty:
		return None

	return missing_df


@with_random_color
def plot_valori_lipsa(missing_df: pd.DataFrame, culoare: str = None) -> go.Figure | None:
	variabila = "Variabilă"
	procent = "Procent"
	valori_lipsa = "Valori lipsă"
	titlu = "Procentul valorilor lipsă per coloană"

	if missing_df is None:
		return None

	missing_df = missing_df.sort_values(procent, ascending=False)

	customdata = missing_df[[variabila, valori_lipsa, procent]].iloc[::-1]

	fig = go.Figure()

	fig.add_trace(
		go.Bar(
			y=customdata[variabila],
			x=customdata[procent],
			orientation="h",
			marker=dict(color=culoare),
			customdata=customdata.values,
			hovertemplate=(
				"Coloană: %{customdata[0]}<br>"
				"Valori lipsă: %{customdata[1]:,}<br>"
				"Procent: %{customdata[2]:.3f}%<extra></extra>"
			),
		)
	)

	fig.update_layout(
		title=titlu,
		xaxis_title=procent,
		yaxis_title=variabila,
		bargap=0.1,
		margin=dict(l=100, r=20, t=50, b=50),
	)

	return fig
