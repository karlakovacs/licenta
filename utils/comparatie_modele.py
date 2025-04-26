import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ml import METRICI


ACRONIME = {
	"Logistic Regression": "LR",
	"Linear Discriminant Analysis": "LDA",
	"Quadratic Discriminant Analysis": "QDA",
	"K-Nearest Neighbors": "KNN",
	"Support Vector Classifier": "SVC",
	"Decision Tree": "DT",
	"Random Forest": "RF",
	"Balanced Random Forest": "BRF",
	"AdaBoost": "ADA",
	"Gradient Boosting Classifier": "GBC",
	"XGBoost": "XGB",
	"LightGBM": "LGBM",
	"CatBoost": "CB",
	"Multilayer Perceptron": "MLP",
}


def creare_df_metrici(rezultate_modele: dict):
	metrici = {model: valori["metrici"] for model, valori in rezultate_modele.items()}
	df_metrici = pd.DataFrame.from_dict(
		data=metrici,
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

		x_labels = [ACRONIME.get(name, name) for name in sorted_results.Model]
		fig.add_trace(
			go.Bar(
				x=x_labels,
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
	return fig
