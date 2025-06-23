import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .color_decorator import with_random_color


TRADUCERI_LUNI = {
	"January": "Ianuarie",
	"February": "Februarie",
	"March": "Martie",
	"April": "Aprilie",
	"May": "Mai",
	"June": "Iunie",
	"July": "Iulie",
	"August": "August",
	"September": "Septembrie",
	"October": "Octombrie",
	"November": "Noiembrie",
	"December": "Decembrie",
}

TRADUCERI_ZILE = {
	"Monday": "Luni",
	"Tuesday": "Marți",
	"Wednesday": "Miercuri",
	"Thursday": "Joi",
	"Friday": "Vineri",
	"Saturday": "Sâmbătă",
	"Sunday": "Duminică",
}


def descriere_variabila_data(tip: str, serie: pd.Series) -> dict:
	serie = serie.dropna()

	if not pd.api.types.is_datetime64_any_dtype(serie):
		raise ValueError("Coloana nu este de tip datetime.")

	rezultate: dict = {}
	rezultate["tip"] = tip
	rezultate["plot_distributie_temporala"] = plot_distributie_temporala(serie)

	luni_raw = serie.dt.month_name()
	luni_counts = luni_raw.value_counts().sort_index()
	luni_ro = {TRADUCERI_LUNI.get(k, k): int(v) for k, v in luni_counts.items()}

	zile_raw = serie.dt.day_name()
	zile_counts = zile_raw.value_counts()
	zile_ro = {TRADUCERI_ZILE.get(k, k): int(v) for k, v in zile_counts.items()}

	stat = {
		"count": int(serie.count()),
		"min": str(serie.min()),
		"max": str(serie.max()),
		"nunique": int(serie.nunique()),
		"an_min": int(serie.min().year),
		"an_max": int(serie.max().year),
		"luni": luni_ro,
		"zile_saptamana": zile_ro,
	}

	rezultate["statistici"] = stat
	return rezultate


def interpretare_variabila_data(stat: dict) -> str:
	if not stat:
		return "Date insuficiente pentru interpretare."

	an_min = stat.get("an_min")
	an_max = stat.get("an_max")
	luni = stat.get("luni", {})
	zile = stat.get("zile_saptamana", {})

	interpretari = []

	if an_min and an_max:
		if an_max == an_min:
			interpretari.append(f"Datele acoperă anul **{an_min}**.")
		else:
			interpretari.append(f"Datele acoperă perioada **{an_min}–{an_max}**.")

	nr_luni = len(luni)
	if nr_luni == 12:
		interpretari.append("Valori prezente în toate cele 12 luni – distribuție anuală completă.")
	elif nr_luni > 6:
		interpretari.append("Distribuția pe luni este relativ echilibrată.")
	elif nr_luni > 0:
		interpretari.append("Valori concentrate doar în câteva luni – posibil efect sezonier.")
	else:
		interpretari.append("Nu există suficiente informații lunare.")

	if zile:
		zile_ordonate = sorted(zile.items(), key=lambda x: x[1], reverse=True)
		top_zile = [f"{zi} ({nr})" for zi, nr in zile_ordonate]
		interpretari.append(f"Zilele cele mai frecvente sunt: {', '.join(top_zile)}.")
	else:
		interpretari.append("Nu există informații despre zilele săptămânii.")

	return "\n".join(f"- {linie}" for linie in interpretari)


@with_random_color
def plot_distributie_temporala(serie: pd.Series, culoare: str) -> go.Figure:
	serie = serie.dropna()

	if not pd.api.types.is_datetime64_any_dtype(serie):
		raise ValueError("Seria nu este de tip datetime.")

	if serie.dt.year.nunique() > 1:
		grupare = serie.dt.to_period("M").astype(str)
		x_label = "Lună"
	elif serie.dt.day.nunique() > 15:
		grupare = serie.dt.date.astype(str)
		x_label = "Dată"
	else:
		zile_eng = serie.dt.day_name()
		grupare = zile_eng.map(TRADUCERI_ZILE)
		x_label = "Zi a săptămânii"

	distributie = grupare.value_counts().to_dict()

	if x_label == "Zi a săptămânii":
		zile_order = ["Luni", "Marți", "Miercuri", "Joi", "Vineri", "Sâmbătă", "Duminică"]
		distributie = {zi: distributie.get(zi, 0) for zi in zile_order}

	fig = go.Figure()
	fig.add_trace(go.Bar(x=list(distributie.keys()), y=list(distributie.values()), marker=dict(color=culoare)))

	fig.update_layout(
		title="Distribuție temporală", xaxis_title=x_label, yaxis_title="Număr de observații", bargap=0.2, height=400
	)

	return fig


def afisare_descriere_variabila_data(variabila: str, descriere: dict):
	st.header(f"🗓️ `{variabila}` - variabilă de tip dată calendaristică")

	st.subheader(
		"Distribuție temporală",
		help="Vizualizează cum sunt distribuite valorile în timp – pe zile, luni sau ani, în funcție de granularitatea datelor.",
	)

	fig = descriere.get("plot_distributie_temporala")
	if fig:
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Graficul de distribuție nu este disponibil.")

	stat = descriere.get("statistici", {})

	col1, col2 = st.columns(2)

	with col1:
		st.subheader("Interval de timp")
		if stat:
			st.markdown(f"- **Minim**: {stat.get('min', '–')}")
			st.markdown(f"- **Maxim**: {stat.get('max', '–')}")
			st.markdown(f"- **Număr de valori**: {stat.get('count', 0)}")
		else:
			st.warning("Nu există statistici disponibile pentru această variabilă.")

	with col2:
		st.subheader("Interpretare")
		interpretare = interpretare_variabila_data(stat)
		st.markdown(interpretare if interpretare else "Interpretarea nu este disponibilă.")
