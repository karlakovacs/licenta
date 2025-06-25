import html
import json

import pandas as pd

from .conversii import dataframe_to_html, markdown_to_html, matplotlib_to_html, plotly_to_html


def pregatire_set_date(set_date: dict) -> str:
	rezultat: dict = {
		"denumire": set_date.get("denumire", "N/A"),
		"sursa": set_date.get("sursa", "N/A"),
		"tinta": set_date.get("tinta", "N/A"),
	}
	return rezultat


TIPURI_VARIABILE = {
	"NC": "numerică continuă",
	"ND": "numerică discretă",
	"T": "text",
	"D": "dată",
	"C": "categorială",
	"B": "booleană",
}


def pregatire_descrieri(descrieri: dict) -> dict:
	rezultat = {}

	for variabila, info in descrieri.items():
		tip = info.get("tip", "")
		tip_variabila = TIPURI_VARIABILE.get(tip, "necunoscută")
		tip = f"variabilă {tip_variabila}"
		rezultat[variabila] = {"tip": tip}
		rezultat[variabila]["interpretare"] = markdown_to_html(info.get("interpretare", ""))
		if "statistici" in info:
			df = pd.DataFrame(info["statistici"], index=["Valori"])
			rezultat[variabila]["statistici"] = dataframe_to_html(df, index=True)
		if tip == "T":
			continue

		elif tip == "D":
			if "plot_distributie_temporala" in info:
				rezultat[variabila]["plot_distributie_temporala"] = plotly_to_html(info["plot_distributie_temporala"])

		elif tip == "C":
			if "pie_chart" in info:
				rezultat[variabila]["pie_chart"] = plotly_to_html(info["pie_chart"])

		elif tip in ("NC", "ND"):
			if "histograma" in info:
				rezultat[variabila]["histograma"] = plotly_to_html(info["histograma"])
			if "box_plot" in info:
				rezultat[variabila]["box_plot"] = plotly_to_html(info["box_plot"])

	return rezultat


def pregatire_eda(eda: dict) -> dict:
	rezultat: dict = {}

	if "valori_lipsa" in eda:
		if "fig" in eda["valori_lipsa"]:
			rezultat["valori_lipsa"] = plotly_to_html(eda["valori_lipsa"]["fig"])
		else:
			rezultat["valori_lipsa"] = "<p>Nu există valori lipsă în setul de date</p>"

	if "plot_tipuri_variabile" in eda:
		rezultat["plot_tipuri_variabile"] = plotly_to_html(eda["plot_tipuri_variabile"])

	if "distributie_tinta" in eda:
		rezultat["distributie_tinta"] = {}
		rezultat["distributie_tinta"]["pie_chart_tinta"] = plotly_to_html(eda["distributie_tinta"]["pie_chart_tinta"])
		rezultat["distributie_tinta"]["interpretare"] = markdown_to_html(eda["distributie_tinta"]["interpretare"])

	if "descrieri" in eda:
		rezultat["descrieri"] = pregatire_descrieri(eda["descrieri"])

	if "matrice_corelatie" in eda:
		rezultat["matrice_corelatie"] = plotly_to_html(eda["matrice_corelatie"])

	if "plot_variabile_puternic_corelate" in eda:
		rezultat["plot_variabile_puternic_corelate"] = plotly_to_html(eda["plot_variabile_puternic_corelate"])

	return rezultat


def este_valoare_valida(v):
	return v not in (None, "", [], {}, "Niciuna")


def pregatire_preprocesare(preprocesare: dict) -> dict:
	rezultat = {cheie: valoare for cheie, valoare in preprocesare.items() if este_valoare_valida(valoare)}
	return rezultat


def pregatire_modele_antrenate(modele_antrenate: dict) -> dict:
	rezultat: dict = {}

	for model, date in modele_antrenate.items():
		info = {}

		if "hiperparametri" in date:
			info["hiperparametri"] = date["hiperparametri"]

		if "durata_antrenare" in date and date["durata_antrenare"] is not None:
			durata = round(float(date["durata_antrenare"]), 4)
			info["durata_antrenare"] = durata

		rezultat[model] = info

	return rezultat


METRICI_TRADUCERI = {
	"accuracy": "Acuratețe",
	"recall": "Sensibilitate",
	"precision": "Precizie",
	"f1": "Scor F1",
	"roc_auc": "Aria de sub curba ROC",
	"avg_precision": "Precizie medie (AUPRC)",
	"bcr": "Rata de clasificare echilibrată",
	"kappa": "Coeficientul Cohen's Kappa",
	"mcc": "Coeficientul de corelație Matthews",
	"gm": "Medie geometrică",
	"tpr": "TPR",
	"tnr": "TNR",
	"fpr": "FPR",
	"fnr": "FNR",
}


def pregatire_rezultate_modele(rezultate_modele: dict) -> dict:
	rezultat: dict = {}

	for model, date in rezultate_modele.items():
		info: dict = {}

		info["raport_clasificare"] = dataframe_to_html(date.get("raport_clasificare"), True)

		dict_metrici: dict = date.get("metrici", {})
		info["metrici"] = {
			METRICI_TRADUCERI.get(cheie, cheie): round(valoare, 4) for cheie, valoare in dict_metrici.items()
		}

		if "matrice_confuzie" in date and date["matrice_confuzie"] is not None:
			info["matrice_confuzie"] = plotly_to_html(date["matrice_confuzie"])

		if "roc" in date and date["roc"] is not None:
			info["roc"] = plotly_to_html(date["roc"])

		if "pr" in date and date["pr"] is not None:
			info["pr"] = plotly_to_html(date["pr"])

		rezultat[model] = info
	return rezultat


def pregatire_xai(instante: dict, xai: dict) -> dict:
	rezultate_finale = {}

	for idx_str, instanta_info in instante.items():
		idx = int(idx_str)
		rezultat = {
			"date": dataframe_to_html(instanta_info.get("date")),
			"y_true": instanta_info.get("y_true", None),
		}

		for model, predictii in instanta_info.items():
			if model in ("date", "y_true"):
				continue

			rezultat_model = {
				"y_pred": predictii.get("y_pred"),
				"y_prob": predictii.get("y_prob"),
			}

			xai_model = xai.get(model, {})
			for metoda, explicatii in xai_model.items():
				if idx_str in explicatii:
					xai_val = explicatii[idx_str]

					if metoda == "SHAP":
						rezultat_model[metoda] = {
							"figura": matplotlib_to_html(xai_val[0]),
							"interpretare": markdown_to_html(xai_val[1]),
						}

					elif metoda == "LIME":
						rezultat_model[metoda] = {
							"figura": plotly_to_html(xai_val[0]),
							"interpretare": markdown_to_html(xai_val[1]),
						}

					elif metoda == "DiCE ML":
						rezultat_model[metoda] = {"interpretare": markdown_to_html(xai_val["interpretari"])}

			rezultat[model] = rezultat_model

		rezultate_finale[idx] = rezultat

	return rezultate_finale


def pregatire_comparatii_modele(comparatii_modele: dict) -> dict:
	comparatii_modele_final: dict = {}
	comparatii_modele_final["df_comparatii"] = dataframe_to_html(comparatii_modele["df_comparatii"])
	comparatii_modele_final["grafic"] = plotly_to_html(comparatii_modele["grafic"])
	return comparatii_modele_final


def pregatire_date_raport(date_raport: dict) -> dict:
	date_raport_html: dict = {}

	if "set_date" in date_raport and date_raport["set_date"] is not None:
		set_date: dict = date_raport["set_date"]
		date_raport_html["set_date"] = pregatire_set_date(set_date)

	if "eda" in date_raport and date_raport["eda"] is not None:
		eda: dict = date_raport["eda"]
		date_raport_html["eda"] = pregatire_eda(eda)

	if "preprocesare" in date_raport and date_raport["preprocesare"] is not None:
		date_raport_html["preprocesare"] = pregatire_preprocesare(date_raport["preprocesare"])

	if "modele_antrenate" in date_raport and date_raport["modele_antrenate"] is not None:
		modele_antrenate: dict = date_raport["modele_antrenate"]
		date_raport_html["modele_antrenate"] = pregatire_modele_antrenate(modele_antrenate)

	if "rezultate_modele" in date_raport and date_raport["rezultate_modele"] is not None:
		rezultate_modele: dict = date_raport["rezultate_modele"]
		date_raport_html["rezultate_modele"] = pregatire_rezultate_modele(rezultate_modele)

	if "comparatii_modele" in date_raport and date_raport["comparatii_modele"] is not None:
		comparatii_modele: dict = date_raport["comparatii_modele"]
		date_raport_html["comparatii_modele"] = pregatire_comparatii_modele(comparatii_modele)

	if (
		"xai_test" in date_raport
		and "instante_test" in date_raport
		and date_raport["xai_test"] is not None
		and date_raport["instante_test"] is not None
	):
		xai_test: dict = date_raport["xai_test"]
		instante_test: dict = date_raport["instante_test"]
		date_raport_html["xai_test"] = pregatire_xai(instante_test, xai_test)

	if (
		"xai_predictii" in date_raport
		and "instante_predictii" in date_raport
		and date_raport["xai_predictii"] is not None
		and date_raport["instante_predictii"] is not None
	):
		xai_predictii: dict = date_raport["xai_predictii"]
		instante_predictii: dict = date_raport["instante_predictii"]
		date_raport_html["xai_predictii"] = pregatire_xai(instante_predictii, xai_predictii)

	return date_raport_html
