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


METRICI_INFO = {
	"Acuratețe": {
		"descriere": "Proporția totală de predicții corecte.",
		"formula": r"Accuracy = \frac{TP + TN}{TP + TN + FP + FN}",
		"utilitate": "Utilă când clasele sunt echilibrate. Poate fi înșelătoare pe date dezechilibrate.",
	},
	"Sensibilitate": {
		"descriere": "Proporția de exemple pozitive detectate corect.",
		"formula": r"Recall = \frac{TP}{TP + FN}",
		"utilitate": "Critică atunci când rata de detecție a clasei pozitive este importantă (ex: boli).",
	},
	"Precizie": {
		"descriere": "Proporția de predicții pozitive care sunt corecte.",
		"formula": r"Precision = \frac{TP}{TP + FP}",
		"utilitate": "Importantă când costul unui fals pozitiv e mare (ex: alarme false).",
	},
	"Scor F1": {
		"descriere": "Media armonică dintre precizie și sensibilitate.",
		"formula": r"F1 = 2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}",
		"utilitate": "Utile când ai nevoie de echilibru între precizie și sensibilitate.",
	},
	"Aria de sub curba ROC": {
		"descriere": "Măsoară capacitatea modelului de a separa clasele.",
		"formula": None,
		"utilitate": "Furnizează o imagine de ansamblu, dar poate ascunde probleme în seturi dezechilibrate.",
	},
	"Precizie medie (AUPRC)": {
		"descriere": "Aria sub curba Precizie-Recall.",
		"formula": None,
		"utilitate": "Mult mai relevant decât ROC-AUC pentru date dezechilibrate.",
	},
	"Rata de clasificare echilibrată": {
		"descriere": "Media dintre sensibilitate și specificitate.",
		"formula": r"Balanced\ Accuracy = \frac{TPR + TNR}{2}",
		"utilitate": "Ajustează acuratețea pentru dezechilibre de clasă.",
	},
	"Coeficientul Cohen's Kappa": {
		"descriere": "Acuratețe ajustată pentru șansă.",
		"formula": r"Kappa = \frac{p_o - p_e}{1 - p_e}",
		"utilitate": "Evaluează performanța față de clasificare întâmplătoare.",
	},
	"Coeficientul de corelație Matthews": {
		"descriere": "Măsoară corelația între predicții și etichete reale.",
		"formula": r"MCC = \frac{TP \cdot TN - FP \cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}",
		"utilitate": "Recomandat pentru clasificare binară dezechilibrată.",
	},
	"Medie geometrică": {
		"descriere": "Rădăcina pătrată din TPR × TNR.",
		"formula": r"G\_mean = \sqrt{TPR \cdot TNR}",
		"utilitate": "Penalizează dezechilibrele mari între clase.",
	},
	"TPR": {
		"descriere": "Rata de detecție a clasei pozitive.",
		"formula": r"TPR = \frac{TP}{TP + FN}",
		"utilitate": "Sinonim cu sensibilitatea. Important în detectarea corectă a clasei pozitive.",
	},
	"TNR": {
		"descriere": "Proporția de negative clasificate corect.",
		"formula": r"TNR = \frac{TN}{TN + FP}",
		"utilitate": "Important pentru a evita alarme false (fals pozitive).",
	},
	"FPR": {
		"descriere": "Proporția de negative clasificate greșit ca pozitive.",
		"formula": r"FPR = \frac{FP}{FP + TN}",
		"utilitate": "Importantă când falsurile pozitive au cost mare.",
	},
	"FNR": {
		"descriere": "Proporția de pozitive ratate.",
		"formula": r"FNR = \frac{FN}{FN + TP}",
		"utilitate": "Importantă în aplicații unde ratele de rată trebuie minimizate (ex: boli).",
	},
}


def calcul_raport_clasificare(y_true, y_pred):
	report = classification_report(y_true, y_pred, output_dict=True)
	df = pd.DataFrame(report).transpose()
	return df


def calcul_metrici(y_true, y_pred, y_prob) -> dict:
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

	metrici = {
		"accuracy": accuracy,
		"recall": recall,
		"precision": precision,
		"f1": f1,
		"roc_auc": roc_auc,
		"avg_precision": avg_precision,
		"bcr": bcr,
		"kappa": kappa,
		"mcc": mcc,
		"gm": gm,
		"tpr": tpr,
		"tnr": tnr,
		"fpr": fpr,
		"fnr": fnr,
	}

	return metrici


def afisare_metrici(metrici: dict):
	col1, col2, col3, col4 = st.columns(4)
	for idx, (key, value) in enumerate(zip(METRICI, metrici.values())):
		col = [col1, col2, col3, col4][idx % 4]
		info = METRICI_INFO.get(key, {})
		formula = info.get("formula", "")
		if formula:
			formula_text = f"${formula}$"
		else:
			formula_text = ""
		help_text = f"{info.get('descriere', '')}\n\n{formula_text}\n\n{info.get('utilitate', '')}"
		col.metric(label=key, value=f"{value:.4f}", help=help_text)


def plot_matrice_confuzie(y_true, y_pred):
	cm = confusion_matrix(y_true, y_pred)
	cm = cm[::-1]

	fig = go.Figure(
		data=go.Heatmap(
			z=cm,
			x=["Prezis: Legitimă", "Prezis: Fraudă"],
			y=["Actual: Fraudă", "Actual: Legitimă"],
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
		xaxis=dict(tickmode="array", tickvals=[0, 1], ticktext=["Prezis: Legitimă", "Prezis: Fraudă"]),
		yaxis=dict(tickmode="array", tickvals=[0, 1], ticktext=["Actual: Fraudă", "Actual: Legitimă"]),
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
			line=dict(color="orange", dash="dash", width=3),
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
