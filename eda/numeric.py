import pandas as pd
import plotly.graph_objects as go
from scipy.stats import kurtosis, skew
import streamlit as st

from .color_decorator import with_random_color


def descriere_variabila_numerica(tip: str, serie: pd.Series):
	serie = serie.dropna()
	rezultate: dict = {}
	rezultate["tip"] = tip
	rezultate["histograma"] = plot_histograma(serie)
	rezultate["box_plot"] = plot_box_plot(serie)
	rezultate["statistici"] = {
		"Număr obs.": int(serie.count()),
		"Minim": float(serie.min()),
		"Maxim": float(serie.max()),
		"Medie": float(serie.mean()),
		"Mediană": float(serie.median()),
		"Mod": float(serie.mode().iloc[0]) if not serie.mode().empty else None,
		"Abatere standard": float(serie.std()),
		"Varianță": float(serie.var()),
		"Coeficient de variație": float(serie.std() / serie.mean()) if serie.mean() != 0 else None,
		"Asimetrie": float(skew(serie)),
		"Kurtosis": float(kurtosis(serie)),
		"Q1": float(serie.quantile(0.25)),
		"Q3": float(serie.quantile(0.75)),
		"IQR": float(serie.quantile(0.75) - serie.quantile(0.25)),
		"Număr valori unice": int(serie.nunique()),
	}
	rezultate["interpretare"] = interpretare_variabila_numerica(rezultate["statistici"])
	return rezultate


@with_random_color
def plot_histograma(serie: pd.Series, culoare: str) -> go.Figure:
	nume_variabila = serie.name

	frecventa = "Frecvență"
	titlu = f"Histogramă pentru '{nume_variabila}'"
	fig = go.Figure(data=[go.Histogram(x=serie, marker=dict(color=culoare))])

	fig.update_layout(
		title=titlu,
		xaxis_title=nume_variabila,
		yaxis_title=frecventa,
		bargap=0.1,
		template="plotly_white",
	)

	return fig


@with_random_color
def plot_box_plot(serie: pd.Series, culoare: str) -> go.Figure:
	nume_variabila = serie.name
	titlu = f"Box plot pentru '{nume_variabila}'"
	fig = go.Figure()
	fig.add_trace(
		go.Box(
			y=serie,
			name=nume_variabila,
			boxmean=True,
			marker=dict(color=culoare),
		)
	)
	fig.update_layout(title=titlu, yaxis_title=nume_variabila)
	return fig


def interpretare_variabila_numerica(statistici: dict) -> str:
	if not statistici:
		return "Nu există suficiente date pentru interpretare."

	medie = statistici["Medie"]
	mediana = statistici["Mediană"]
	std = statistici["Abatere standard"]
	cv = statistici["Coeficient de variație"]
	skewness = statistici["Asimetrie"]
	kurt = statistici["Kurtosis"]
	iqr = statistici["IQR"]
	q1 = statistici["Q1"]
	q3 = statistici["Q3"]
	min_val = statistici["Minim"]
	max_val = statistici["Maxim"]

	interpretari = []

	if abs(skewness) < 0.5:
		interpretari.append("Distribuția este aproximativ simetrică.")
	elif skewness > 0.5:
		interpretari.append("Distribuția este asimetrică pozitiv (prea multe valori mici, coadă în dreapta).")
	else:
		interpretari.append("Distribuția este asimetrică negativ (prea multe valori mari, coadă în stânga).")

	if abs(medie - mediana) < 0.1 * std:
		interpretari.append("Media și mediana sunt apropiate, ceea ce sugerează o distribuție echilibrată.")
	else:
		directie = "mai mare" if medie > mediana else "mai mică"
		interpretari.append(f"Media este semnificativ {directie} decât mediana – posibil efect al valorilor extreme.")

	if cv is not None:
		if cv < 0.1:
			interpretari.append("Variabilitatea este foarte scăzută.")
		elif cv < 0.3:
			interpretari.append("Variabilitatea este moderată.")
		else:
			interpretari.append("Variabilitatea este ridicată – valorile sunt răspândite.")

	lower_bound = q1 - 1.5 * iqr
	upper_bound = q3 + 1.5 * iqr
	num_out_min = sum([min_val < lower_bound])
	num_out_max = sum([max_val > upper_bound])
	if num_out_min or num_out_max:
		interpretari.append("Există valori extreme (outlieri) în date.")
	else:
		interpretari.append("Nu au fost identificate valori extreme pe baza IQR.")

	if abs(kurt - 3) <= 0.05:
		interpretari.append("Distribuția are o curtosis apropiată de cea normală (mesokurtică).")
	elif kurt > 3:
		interpretari.append("Distribuția este leptokurtică – are cozi mai groase decât normalul (mai mulți outlieri).")
	else:
		interpretari.append("Distribuția este platikurtică – mai aplatizată decât normalul.")

	return "- " + "\n- ".join(interpretari)


def afisare_descriere_variabila_numerica(variabila: str, descriere: dict):
	tip_brut = descriere.get("tip", "N/A")
	tip_numeric = "continuă" if tip_brut == "NC" else "discretă"
	histo = descriere.get("histograma")
	box = descriere.get("box_plot")
	statistici = descriere.get("statistici", {})
	interpretare = descriere.get("interpretare", None)

	st.header(f"🔢 `{variabila}` - variabilă numerică {tip_numeric}")

	col1, col2 = st.columns(2)

	with col1:
		st.subheader("Histogramă", help="Distribuția valorilor pe intervale.")
		if histo:
			st.plotly_chart(histo, use_container_width=True)
		else:
			st.info("Histogramă indisponibilă.")

	with col2:
		st.subheader("Box plot", help="Vizualizarea medianei, quartilelor și a valorilor extreme.")
		if box:
			st.plotly_chart(box, use_container_width=True)
		else:
			st.info("Box plot indisponibil.")

	col1_, col2_ = st.columns(2)

	with col1_:
		st.subheader("Statistici")
		if statistici:
			df_stats = pd.DataFrame(statistici, index=["Valori"]).T
			st.dataframe(df_stats, use_container_width=True)
		else:
			st.warning("Nu există statistici pentru această variabilă.")

	with col2_:
		st.subheader("Interpretare")
		st.write(interpretare or "Interpretarea nu este disponibilă.")
