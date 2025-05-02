from xai.lime import explanation_plotly

from .conversii import *


def pregatire_set_date(set_date: dict) -> dict:
	set_date_final: dict = {
		"denumire": set_date.get("denumire", "N/A"),
		"sursa": set_date.get("sursa", "N/A"),
		"tinta": set_date.get("tinta", "N/A"),
	}
	return set_date_final


def pregatire_eda(eda: dict, format_pdf: bool = False) -> dict:
	eda_final: dict = {}

	if "describe_numeric" in eda:
		eda_final["describe_numeric"] = dataframe_to_html(eda["describe_numeric"], format_pdf)

	if "describe_categorical" in eda:
		eda_final["describe_categorical"] = dataframe_to_html(eda["describe_categorical"], format_pdf)

	if "plot_tipuri_variabile" in eda:
		eda_final["plot_tipuri_variabile"] = plotly_to_html(eda["plot_tipuri_variabile"], format_pdf)

	if "pie_chart_tinta" in eda:
		eda_final["pie_chart_tinta"] = plotly_to_html(eda["pie_chart_tinta"], format_pdf)

	if "pie_charts" in eda:
		eda_final["pie_charts"] = {}
		for variabila, fig in eda["pie_charts"].items():
			eda_final["pie_charts"][variabila] = plotly_to_html(fig, format_pdf)

	if "histograme" in eda:
		eda_final["histograme"] = {}
		for variabila, fig in eda["histograme"].items():
			eda_final["histograme"][variabila] = plotly_to_html(fig, format_pdf)

	if "box_plots" in eda:
		eda_final["box_plots"] = {}
		for variabila, fig in eda["box_plots"].items():
			eda_final["box_plots"][variabila] = plotly_to_html(fig, format_pdf)

	if "plot_matrice_corelatie" in eda and eda["plot_matrice_corelatie"].get("fig"):
		eda_final["plot_matrice_corelatie"] = plotly_to_html(eda["plot_matrice_corelatie"]["fig"], format_pdf)

	if "valori_lipsa" in eda and eda["valori_lipsa"].get("fig"):
		eda_final["valori_lipsa"] = plotly_to_html(eda["valori_lipsa"]["fig"], format_pdf)

	if "plot_variabile_puternic_corelate" in eda:
		eda_final["plot_variabile_puternic_corelate"] = plotly_to_html(
			eda["plot_variabile_puternic_corelate"], format_pdf
		)

	return eda_final


def pregatire_modele_antrenate(modele_antrenate: dict) -> dict:
	modele_antrenate_final: dict = {}
	for model, date in modele_antrenate.items():
		date_selectate: dict = {k: v for k, v in date.items() if k in ["hiperparametri", "timp"]}
		modele_antrenate_final[model] = date_selectate
	return modele_antrenate_final


def pregatire_rezultate_modele(rezultate_modele: dict, format_pdf: bool = False) -> dict:
	rezultate_modele_final: dict = {}

	for model, date in rezultate_modele.items():
		model_html: dict = {}

		model_html["raport_clasificare"] = dataframe_to_html(date.get("raport_clasificare"))

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
		lista_metrici = date.get("metrici")
		model_html["metrici"] = {metrica: valoare for metrica, valoare in zip(METRICI, lista_metrici)}

		if "matrice_confuzie" in date and date["matrice_confuzie"] is not None:
			model_html["matrice_confuzie"] = plotly_to_html(date["matrice_confuzie"], format_pdf)

		if "roc" in date and date["roc"] is not None:
			model_html["roc"] = plotly_to_html(date["roc"], format_pdf)

		if "pr" in date and date["pr"] is not None:
			model_html["pr"] = plotly_to_html(date["pr"], format_pdf)

		rezultate_modele_final[model] = model_html
	return rezultate_modele_final


def pregatire_xai(xai: dict, format_pdf: bool = False) -> dict:
	xai_final: dict = {}

	for model, date in xai.items():
		model_html: dict = {}

		if "shap" in date and "plots" in date["shap"]:
			shap_plots = date["shap"]["plots"]
			model_html["shap"] = {}

			for tip_plot, plot_obj in shap_plots.items():
				if isinstance(plot_obj, dict):
					model_html["shap"][tip_plot] = {}
					for idx, fig in plot_obj.items():
						if fig is not None:
							model_html["shap"][tip_plot][idx] = matplotlib_to_html(fig)
				else:
					if plot_obj is not None:
						model_html["shap"][tip_plot] = matplotlib_to_html(plot_obj)

		if "lime" in date and "explanations" in date["lime"]:
			model_html["lime"] = {}
			for idx, exp in date["lime"]["explanations"].items():
				if exp is not None:
					model_html["lime"][idx] = plotly_to_html(explanation_plotly(exp), format_pdf)

		if "dice" in date and "counterfactuals" in date["dice"]:
			model_html["dice"] = {}
			for idx, instance in date["dice"]["counterfactuals"].items():
				if instance is None:
					continue

				predictie = instance.get("predictie")
				cf_df = instance.get("cf_df")
				explicatii = instance.get("explicatii")

				if predictie is None and cf_df is None and explicatii is None:
					continue

				model_html["dice"][idx] = {
					"predictie": predictie,
					"cf_df": dataframe_to_html(cf_df, format_pdf) if cf_df is not None else "",
					"explicatii": explicatii_dice_to_text(explicatii),
				}

		xai_final[model] = model_html
	return xai_final


def pregatire_date_raport(date_raport: dict, format_pdf: bool = False) -> dict:
	date_raport_html: dict = {}

	if "set_date" in date_raport and date_raport["set_date"] is not None:
		set_date: dict = date_raport["set_date"]
		date_raport_html["set_date"] = pregatire_set_date(set_date)

	if "eda" in date_raport and date_raport["eda"] is not None:
		eda: dict = date_raport["eda"]
		date_raport_html["eda"] = pregatire_eda(eda, format_pdf)

	if "procesare" in date_raport and date_raport["procesare"] is not None:
		date_raport_html["procesare"] = date_raport["procesare"]

	if "modele_antrenate" in date_raport and date_raport["modele_antrenate"] is not None:
		modele_antrenate: dict = date_raport["modele_antrenate"]
		date_raport_html["modele_antrenate"] = pregatire_modele_antrenate(modele_antrenate)

	if "rezultate_modele" in date_raport and date_raport["rezultate_modele"] is not None:
		rezultate_modele: dict = date_raport["rezultate_modele"]
		date_raport_html["rezultate_modele"] = pregatire_rezultate_modele(rezultate_modele, format_pdf)

	if "xai" in date_raport and date_raport["xai"] is not None:
		xai: dict = date_raport["xai"]
		date_raport_html["xai"] = pregatire_xai(xai, format_pdf)

	if "grafic_comparativ" in date_raport and date_raport["grafic_comparativ"] is not None:
		date_raport_html["grafic_comparativ"] = plotly_to_html(date_raport["grafic_comparativ"], format_pdf)

	return date_raport_html
