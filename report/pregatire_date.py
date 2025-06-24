import html
import json

import pandas as pd

from .conversii import dataframe_to_html, markdown_to_html, matplotlib_to_html, plotly_to_html


def pregatire_set_date(set_date: dict) -> str:
	denumire = set_date.get("denumire", "N/A")
	sursa = set_date.get("sursa", "N/A")
	tinta = set_date.get("tinta", "N/A")

	html_string = f"""
		<p><strong>Denumire set de date:</strong> <code>{denumire}</code></p>
		<p><strong>Sursă:</strong> <code>{sursa}</code></p>
		<p><strong>Variabilă țintă:</strong> <code>{tinta}</code></p>
	"""
	return html_string.strip()


def pregatire_descrieri(descrieri: dict, format_pdf: bool = False) -> dict:
	rezultat = {}

	for variabila, info in descrieri.items():
		tip = info.get("tip", "")
		rezultat[variabila] = {"tip": tip}
		rezultat[variabila]["interpretare"] = markdown_to_html(info.get("interpretare", ""))
		if "statistici" in info:
			df = pd.DataFrame(info["statistici"], index=["Valori"]).T
			rezultat[variabila]["statistici"] = dataframe_to_html(df)
		if tip == "T":
			continue

		elif tip == "D":
			if "plot_distributie_temporala" in info:
				rezultat[variabila]["plot_distributie_temporala"] = plotly_to_html(
					info["plot_distributie_temporala"], format_pdf
				)

		elif tip == "C":
			if "pie_chart" in info:
				rezultat[variabila]["pie_chart"] = plotly_to_html(info["pie_chart"], format_pdf)

		elif tip in ("NC", "ND"):
			if "histograma" in info:
				rezultat[variabila]["histograma"] = plotly_to_html(info["histograma"], format_pdf)
			if "box_plot" in info:
				rezultat[variabila]["box_plot"] = plotly_to_html(info["box_plot"], format_pdf)

	return rezultat


def pregatire_eda(eda: dict, format_pdf: bool = False) -> dict:
	eda_final: dict = {}

	if "valori_lipsa" in eda:
		eda_final["valori_lipsa"] = plotly_to_html(eda["valori_lipsa"]["fig"], format_pdf)

	if "plot_tipuri_variabile" in eda:
		eda_final["plot_tipuri_variabile"] = plotly_to_html(eda["plot_tipuri_variabile"], format_pdf)

	if "distributie_tinta" in eda:
		eda_final["distributie_tinta"] = {}
		eda_final["distributie_tinta"]["pie_chart_tinta"] = plotly_to_html(
			eda["distributie_tinta"]["pie_chart_tinta"], format_pdf
		)
		eda_final["distributie_tinta"]["interpretare"] = markdown_to_html(
			eda["distributie_tinta"]["interpretare"]
		)

	if "descrieri" in eda:
		eda_final["descrieri"] = pregatire_descrieri(eda["descrieri"], format_pdf)

	if "matrice_corelatie" in eda:
		eda_final["matrice_corelatie"] = plotly_to_html(eda["matrice_corelatie"], format_pdf)

	if "plot_variabile_puternic_corelate" in eda:
		eda_final["plot_variabile_puternic_corelate"] = plotly_to_html(
			eda["plot_variabile_puternic_corelate"], format_pdf
		)

	return eda_final


def pregatire_procesare(procesare: dict) -> str:
	html_string = ""

	if cols := procesare.get("coloane_eliminate"):
		html_string += f"<p><strong>Coloane eliminate:</strong> {', '.join(f'<code>{col}</code>' for col in cols)}</p>"

	if procesare.get("eliminare_duplicate"):
		html_string += "<p><strong>Eliminare duplicate:</strong> <code>Activată</code></p>"

	if procesare.get("eliminare_randuri_nan"):
		html_string += "<p><strong>Eliminare rânduri cu valori lipsă:</strong> <code>Activată</code></p>"

	if out := procesare.get("outlieri"):
		html_string += (
			f"<p><strong>Tratament outlieri:</strong> "
			f"Detectare cu <code>{out.get('detectie')}</code>, acțiune: <code>{out.get('actiune')}</code></p>"
		)

	if vl := procesare.get("valori_lipsa"):
		html_string += (
			"<p><strong>Imputarea valorilor lipsă:</strong><br>"
			f"- Strategie pentru variabilele numerice: <code>{vl.get('strategie_numerice')}</code>, "
			f"valoare fixă: <code>{vl.get('valoare_fixa_numerice')}</code><br>"
			f"- Strategie pentru variabilele categoriale: <code>{vl.get('strategie_categoriale')}</code>, "
			f"valoare fixă: <code>{vl.get('valoare_fixa_categoriale')}</code></p>"
		)

	if binare := procesare.get("coloane_binare"):
		linie = ", ".join(f"<code>{k}=True</code>" for k, v in binare.items() if v)
		html_string += f"<p><strong>Conversii binare:</strong> {linie}</p>"

	if dt := procesare.get("datetime"):
		comp = ", ".join(f"<code>{c}</code>" for c in dt.get("componente", []))
		cols = ", ".join(f"<code>{c}</code>" for c in dt.get("coloane", []))
		html_string += f"<p><strong>Conversii dată/timp:</strong> coloane: {cols}; componente extrase: {comp}</p>"

	if enc := procesare.get("encoding"):
		html_string += (
			"<p><strong>Codificare pentru variabilele categoriale:</strong> "
			f"Variabilele vor fi codificate folosind One Hot Encoding, cu limita: <code>{enc.get('max_categorii')}</code> categorii<br>"
		)
		coloane_label = enc.get("coloane_label", {})
		if coloane_label:
			html_string += "<p><strong>Label encoding aplicat pe:</strong><ul>"
			for var, ordonare in coloane_label.items():
				html_string += f"<li><code>{var}</code>: ["
				etichete = [f"<code>{eticheta}</code>" for eticheta in ordonare]
				html_string += ", ".join(etichete) + "]</li>"
			html_string += "</ul></p>"

	html_string += f"<p><strong>Tratament pentru dezechilibrul dintre clase:</strong> <code>{procesare.get('dezechilibru')}</code></p>"
	html_string += (
		f"<p><strong>Tehnică de scalare a variabilelor numerice:</strong> <code>{procesare.get('scalare')}</code></p>"
	)

	if impartire := procesare.get("impartire"):
		html_string += (
			f"<p><strong>Împărțire train/test:</strong> "
			f"test = <code>{impartire.get('proportie_test')}</code>, "
			f"stratificat = <code>{impartire.get('stratificat')}</code>, "
			f"variabilă țintă = <code>{impartire.get('tinta')}</code></p>"
		)

	return html_string.strip()


def pregatire_modele_antrenate(modele_antrenate: dict) -> dict:
	html_string = ""

	for model, date in modele_antrenate.items():
		html_string += f"<h4>{html.escape(model)}</h4>"

		hiperparametri = date.get("hiperparametri", {})
		if hiperparametri:
			param_str = json.dumps(hiperparametri, indent=2, ensure_ascii=False)
			html_string += "<p><strong>Hiperparametri:</strong></p>"
			html_string += f"<pre><code>{html.escape(param_str)}</code></pre>"

		durata = date.get("durata_antrenare")
		if durata is not None:
			html_string += f"<p><strong>Durata antrenării:</strong> <code>{html.escape(str(durata))}</code> secunde</p>"

	html_string += "</div>"
	return html_string


def pregatire_rezultate_modele(rezultate_modele: dict, format_pdf: bool = False) -> dict:
	rezultate_modele_final: dict = {}

	for model, date in rezultate_modele.items():
		model_html: dict = {}

		model_html["raport_clasificare"] = dataframe_to_html(date.get("raport_clasificare"))

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

		dict_metrici: dict = date.get("metrici", {})
		model_html["metrici"] = {
			METRICI_TRADUCERI.get(cheie, cheie): round(valoare, 4) for cheie, valoare in dict_metrici.items()
		}

		if "matrice_confuzie" in date and date["matrice_confuzie"] is not None:
			model_html["matrice_confuzie"] = plotly_to_html(date["matrice_confuzie"], format_pdf)

		if "roc" in date and date["roc"] is not None:
			model_html["roc"] = plotly_to_html(date["roc"], format_pdf)

		if "pr" in date and date["pr"] is not None:
			model_html["pr"] = plotly_to_html(date["pr"], format_pdf)

		rezultate_modele_final[model] = model_html
	return rezultate_modele_final


def pregatire_xai(instante: dict, xai: dict, format_pdf: bool = False) -> dict:
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
							"figura": plotly_to_html(xai_val[0], format_pdf),
							"interpretare": markdown_to_html(xai_val[1]),
						}

					elif metoda == "DiCE ML":
						rezultat_model[metoda] = {"interpretare": markdown_to_html(xai_val["interpretari"])}

			rezultat[model] = rezultat_model

		rezultate_finale[idx] = rezultat

	return rezultate_finale


def pregatire_comparatii_modele(comparatii_modele: dict, format_pdf: bool = False) -> dict:
	comparatii_modele_final: dict = {}
	comparatii_modele_final["df_comparatii"] = dataframe_to_html(comparatii_modele["df_comparatii"], format_pdf)
	comparatii_modele_final["grafic"] = plotly_to_html(comparatii_modele["grafic"], format_pdf)
	return comparatii_modele_final


def pregatire_date_raport(date_raport: dict, format_pdf: bool = False) -> dict:
	date_raport_html: dict = {}

	if "set_date" in date_raport and date_raport["set_date"] is not None:
		set_date: dict = date_raport["set_date"]
		date_raport_html["set_date"] = pregatire_set_date(set_date)

	if "eda" in date_raport and date_raport["eda"] is not None:
		eda: dict = date_raport["eda"]
		date_raport_html["eda"] = pregatire_eda(eda, format_pdf)

	if "procesare" in date_raport and date_raport["procesare"] is not None:
		date_raport_html["procesare"] = pregatire_procesare(date_raport["procesare"])

	if "modele_antrenate" in date_raport and date_raport["modele_antrenate"] is not None:
		modele_antrenate: dict = date_raport["modele_antrenate"]
		date_raport_html["modele_antrenate"] = pregatire_modele_antrenate(modele_antrenate)

	if "rezultate_modele" in date_raport and date_raport["rezultate_modele"] is not None:
		rezultate_modele: dict = date_raport["rezultate_modele"]
		date_raport_html["rezultate_modele"] = pregatire_rezultate_modele(rezultate_modele, format_pdf)

	if "comparatii_modele" in date_raport:
		comparatii_modele: dict = date_raport["comparatii_modele"]
		date_raport_html["comparatii_modele"] = pregatire_comparatii_modele(comparatii_modele, format_pdf)

	if "xai_test" in date_raport and "instante_test" in date_raport:
		xai_test: dict = date_raport["xai_test"]
		instante_test: dict = date_raport["instante_test"]
		date_raport_html["xai_test"] = pregatire_xai(instante_test, xai_test, format_pdf)

	if "xai_predictii" in date_raport and "instante_predictii" in date_raport:
		xai_predictii: dict = date_raport["xai_predictii"]
		instante_predictii: dict = date_raport["instante_predictii"]
		date_raport_html["xai_predictii"] = pregatire_xai(instante_predictii, xai_predictii, format_pdf)

	return date_raport_html
