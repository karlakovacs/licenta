import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def plot_pie_chart(serie: pd.Series, max_categorii: int = 25) -> go.Figure:
	categorie = "Categorie"
	numar_aparitii = "Număr de apariții"
	titlu = f"Distribuția valorilor pentru '{serie.name}'"

	if serie.nunique() > max_categorii:
		st.warning("Prea multe valori unice!")
		return
	else:
		data = serie.value_counts().reset_index()
		data.columns = [categorie, numar_aparitii]

		fig = go.Figure(
			data=[
				go.Pie(
					labels=data[categorie],
					values=data[numar_aparitii],
					textinfo="percent+label",
					hole=0.3,
				)
			]
		)

		fig.update_layout(title=titlu, height=500, template="plotly_white")

		return fig


def descriere_variabila_categoriala(tip: str, serie: pd.Series) -> dict:
	serie = serie.dropna()
	distributie = serie.value_counts()

	rezultate = {
		"tip": tip,
		"pie_chart": plot_pie_chart(serie),
		"statistici": {
			"count": int(serie.count()),
			"distributie": {str(val): int(freq) for val, freq in distributie.items()},
		},
	}
	rezultate["interpretare"] = interpretare_variabila_categoriala(rezultate["statistici"])

	return rezultate


def afisare_descriere_variabila_categoriala(variabila: str, descriere: dict):
	st.header(f"📊 `{variabila}` - variabilă categorială")

	st.subheader(
		"Pie chart",
		help="Reprezentare procentuală a frecvenței fiecărei categorii din variabilă. Util pentru a identifica valorile dominante.",
	)

	fig = descriere.get("pie_chart")
	if fig:
		st.plotly_chart(fig, use_container_width=True)
	else:
		st.info("Graficul nu este disponibil.")

	statistici = descriere.get("statistici", {})

	col1, col2 = st.columns(2)

	with col1:
		st.subheader("Statistici")
		if statistici:
			distributie = statistici.get("distributie", {})
			if distributie:
				df_distributie = pd.DataFrame(list(distributie.items()), columns=["Categorie", "Frecvență"])
				st.dataframe(df_distributie, use_container_width=True)
			st.markdown(f"**Total valori**: {statistici.get('count', 0)}")
		else:
			st.warning("Nu există statistici disponibile.")

	with col2:
		st.subheader("Interpretare")
		interpretare = descriere.get("interpretare", None)
		st.markdown(interpretare or "Interpretarea nu este disponibilă.")


def interpretare_variabila_categoriala(stat: dict) -> str:
	if not stat or "distributie" not in stat:
		return "Date insuficiente pentru interpretare."

	distributie = stat["distributie"]
	count = stat.get("count", sum(distributie.values()))

	num_categorii = len(distributie)
	if count == 0 or num_categorii == 0:
		return "Nu există suficiente date nenule pentru această variabilă."

	valori_ordonate = sorted(distributie.items(), key=lambda x: x[1], reverse=True)
	mod, freq_max = valori_ordonate[0]
	procent_max = round((freq_max / count) * 100, 2)

	interpretari = []

	if num_categorii == 1:
		interpretari.append("Variabila are o singură valoare – nu aduce informație utilă.")
	elif num_categorii <= 3:
		interpretari.append(f"Variabila are doar {num_categorii} categorii – foarte simplu de interpretat.")
	elif num_categorii <= 10:
		interpretari.append(f"Variabila are {num_categorii} categorii – interpretabilă vizual.")
	else:
		interpretari.append(f"Variabila are {num_categorii} categorii – poate necesita grupare sau reducere.")

	if procent_max >= 75:
		interpretari.append(
			f"Categoria dominantă este `{mod}` cu {procent_max}% din apariții – distribuție dezechilibrată."
		)
	elif procent_max >= 50:
		interpretari.append(f"Categoria `{mod}` este frecventă ({procent_max}%), dar nu exclusivă.")
	elif procent_max >= 30:
		interpretari.append(f"Categoria principală (`{mod}`) are o pondere moderată ({procent_max}%).")
	else:
		interpretari.append("Distribuția între categorii este relativ echilibrată.")

	return "\n".join(f"- {linie}" for linie in interpretari)


def interpretare_tinta(y: pd.Series) -> str:
	y = y.dropna()
	total = len(y)
	frecvente = y.value_counts()
	procentuale = y.value_counts(normalize=True) * 100

	if total == 0:
		return "Variabila țintă nu conține date disponibile."

	if len(frecvente) == 1:
		return f"Toate valorile țintă sunt `{frecvente.index[0]}` – clasificarea binară nu este posibilă."

	clasa_majora = frecvente.index[0]
	p_majora = procentuale.iloc[0]
	clasa_minor = frecvente.index[1]
	p_minor = procentuale.iloc[1]

	interpretari = [
		f"Clasa `{clasa_majora}` reprezintă {p_majora:.2f}% din date.",
		f"Clasa `{clasa_minor}` reprezintă {p_minor:.2f}% din date.",
	]

	dezechilibru = abs(p_majora - p_minor)
	if dezechilibru > 40:
		interpretari.append(
			"Distribuția este **puternic dezechilibrată** – sunt necesare tehnici speciale (resampling, metrici alternative)."
		)
	elif dezechilibru > 20:
		interpretari.append(
			"Distribuția este **moderat dezechilibrată** – urmărește metrici precum `f1-score`, `roc-auc`."
		)
	else:
		interpretari.append(
			"Distribuția între clase este **relativ echilibrată** – evaluarea poate folosi și `accuracy`."
		)

	return "\n".join(f"- {linie}" for linie in interpretari)
