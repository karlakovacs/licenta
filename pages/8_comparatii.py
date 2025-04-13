import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ml import METRICI
from utils import nav_bar


st.set_page_config(layout="wide", page_title="Comparații", page_icon="⚖️")
nav_bar()
st.title("Compararea performanței modelelor")


def get_df_metrici(metrici_modele: dict):
	df_metrici = pd.DataFrame.from_dict(
		data=metrici_modele,
		columns=METRICI,
		orient="index",
	)
	df_metrici.reset_index(inplace=True)
	df_metrici.rename(columns={"index": "Model"}, inplace=True)
	return df_metrici


def grafic_comparativ(df_metrici: pd.DataFrame):
	coloane_metrici = df_metrici.columns[1:]
	num_metrics = len(coloane_metrici) - 1
	cols = 3
	rows = (num_metrics // cols) + (num_metrics % cols > 0)

	fig = make_subplots(rows=rows, cols=cols, subplot_titles=coloane_metrici)

	for i, metric in enumerate(coloane_metrici, start=1):
		row, col = ((i - 1) // cols) + 1, ((i - 1) % cols) + 1
		if metric in ["FPR", "FNR"]:
			sorted_results = df_metrici.sort_values(by=metric, ascending=True)
		else:
			sorted_results = df_metrici.sort_values(by=metric, ascending=False)

		fig.add_trace(
			go.Bar(
				x=sorted_results.Model,
				y=sorted_results[metric],
				name=metric,
			),
			row=row,
			col=col,
		)

	fig.update_layout(
		title="Performanța clasificatorilor",
		height=900,
		width=1200,
		showlegend=False,
		template="plotly_white",
	)
	st.session_state.grafic_comparativ = fig


metrici_modele = st.session_state.metrici_modele
df_metrici = get_df_metrici(metrici_modele)
if "grafic_comparativ" not in st.session_state:
	grafic_comparativ(df_metrici)
st.plotly_chart(st.session_state.grafic_comparativ, use_container_width=False)
