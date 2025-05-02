import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import (
	accuracy_score,
	average_precision_score,
	classification_report,
	cohen_kappa_score,
	confusion_matrix,
	f1_score,
	matthews_corrcoef,
	precision_recall_curve,
	precision_score,
	recall_score,
	roc_auc_score,
	roc_curve,
)
import streamlit as st


METRICI = [
	"Acuratețe",
	"Sensibilitate",
	"Precizie",
	"Scor F1",
	"Aria de sub curba ROC",
	"Precizie medie (AUPRC)",
	"Rata de clasificare echilibrată",
	"Coeficientul Cohen's Kappa",
	"Coeficientul de corelație Matthews",
	"Medie geometrică",
	"TPR",
	"TNR",
	"FPR",
	"FNR",
]


def calcul_raport_clasificare(y_true, y_pred):
	report = classification_report(y_true, y_pred, output_dict=True)
	df = pd.DataFrame(report).transpose()
	return df


def calcul_metrici(y_true, y_pred, y_prob):
	tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

	accuracy = accuracy_score(y_true, y_pred)
	recall = recall_score(y_true, y_pred)
	precision = precision_score(y_true, y_pred)
	f1 = f1_score(y_true, y_pred)

	fpr = fp / (fp + tn) if (fp + tn) != 0 else 0
	tpr = tp / (tp + fn) if (tp + fn) != 0 else 0
	tnr = tn / (tn + fp) if (tn + fp) != 0 else 0
	fnr = fn / (fn + tp) if (fn + tp) != 0 else 0
	bcr = (tpr + tnr) / 2

	try:
		roc_auc = roc_auc_score(y_true, y_prob)
	except ValueError:
		roc_auc = np.nan

	mcc = matthews_corrcoef(y_true, y_pred)
	gm = np.sqrt(tpr * tnr)
	kappa = cohen_kappa_score(y_true, y_pred)
	avg_precision = average_precision_score(y_true, y_prob)

	metrici = [
		accuracy,
		recall,
		precision,
		f1,
		roc_auc,
		avg_precision,
		bcr,
		kappa,
		mcc,
		gm,
		tpr,
		tnr,
		fpr,
		fnr,
	]

	return metrici


def afisare_metrici(metrici):
	col1, col2, col3, col4 = st.columns(4)
	for idx, (key, value) in enumerate(zip(METRICI, metrici)):
		col = [col1, col2, col3, col4][idx % 4]
		col.metric(label=key, value=f"{value:.4f}")


def plot_matrice_confuzie(y_true, y_pred):
	cm = confusion_matrix(y_true, y_pred)
	cm = cm[::-1]

	fig = go.Figure(
		data=go.Heatmap(
			z=cm,
			x=["Prezis 0", "Prezis 1"],
			y=["Actual 0", "Actual 1"],
			colorscale="Blues",
			showscale=False,
			text=cm.astype(str),
			texttemplate="%{text}",
		)
	)

	fig.update_layout(
		title=f"Matrice de confuzie",
		xaxis_title="Prezis",
		yaxis_title="Actual",
		xaxis=dict(tickmode="array", tickvals=[0, 1], ticktext=["Prezis 0", "Prezis 1"]),
		yaxis=dict(tickmode="array", tickvals=[0, 1], ticktext=["Actual 0", "Actual 1"]),
		width=500,
		height=500,
		template="plotly_white",
	)

	return fig


def plot_curba_roc(y_true, y_prob):
	fpr, tpr, _ = roc_curve(y_true, y_prob)
	roc_auc = roc_auc_score(y_true, y_prob)

	fig = go.Figure()

	fig.add_trace(
		go.Scatter(
			x=fpr,
			y=tpr,
			mode="lines",
			name=f"Curba ROC (AUC={roc_auc:.4f})",
			line=dict(color="purple", width=3),
		)
	)

	fig.add_trace(
		go.Scatter(
			x=[0, 1],
			y=[0, 1],
			mode="lines",
			name="Clasificator aleatoriu",
			line=dict(color="yellow", dash="dash", width=3),
		)
	)

	fig.update_layout(
		title=f"Curba ROC",
		xaxis_title="False Positive Rate",
		yaxis_title="True Positive Rate",
		legend=dict(x=0.7, y=0.1),
		width=700,
		height=500,
		template="plotly_white",
	)

	return fig


def plot_curba_pr(y_true, y_prob):
	precision, recall, _ = precision_recall_curve(y_true, y_prob)
	avg_precision = average_precision_score(y_true, y_prob)

	fig = go.Figure()

	fig.add_trace(
		go.Scatter(
			x=recall,
			y=precision,
			mode="lines",
			name=f"Curba PR (AP={avg_precision:.4f})",
			line=dict(color="purple", width=3),
			showlegend=True,
		)
	)

	fig.update_layout(
		title=f"Curba PR",
		xaxis_title="Recall",
		yaxis_title="Precision",
		legend=dict(x=0.01, y=0.1),
		width=700,
		height=500,
		template="plotly_white",
	)

	return fig
