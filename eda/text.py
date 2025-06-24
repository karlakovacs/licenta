import pandas as pd
import streamlit as st


def descriere_variabila_text(tip: str, serie: pd.Series) -> dict:
	serie = serie.dropna()

	count_total = int(serie.count())
	numar_unice = int(serie.nunique())

	top_valori = serie.value_counts().head(10)
	distributie_top = {str(val): int(freq) for val, freq in top_valori.items()}

	rezultate = {
		"tip": tip,
		"statistici": {"count": count_total, "nunique": numar_unice, "top_valori": distributie_top},
	}
	rezultate["interpretare"] = interpretare_variabila_text(rezultate["statistici"])

	return rezultate


def interpretare_variabila_text(stat: dict) -> str:
	if not stat:
		return "Date insuficiente pentru interpretare."

	count = stat.get("count", 0)
	nunique = stat.get("nunique", 0)
	top_valori = stat.get("top_valori", {})

	if count == 0:
		return "Toate valorile sunt lipsă."

	if nunique == 0:
		return "Toate valorile sunt lipsă sau goale."
	elif nunique == 1:
		return "Toate valorile sunt identice – variabila nu oferă informație utilă."

	interpretari = []

	unicitate = nunique / count
	if unicitate > 0.9:
		interpretari.append("Majoritatea valorilor sunt unice – posibilă variabilă de tip ID, nume sau text liber.")
	elif unicitate < 0.1:
		interpretari.append("Variabila conține multe repetiții – posibil codificator sau categorie ascunsă.")
	else:
		interpretari.append("Distribuția valorilor sugerează o variabilă semi-structurată (ex: locații, descrieri).")

	if top_valori:
		valoare_top, frecventa_max = next(iter(top_valori.items()))
		procent = round((frecventa_max / count) * 100, 2)
		interpretari.append(f"Valoarea cea mai frecventă (`{valoare_top}`) apare în {procent}% dintre înregistrări.")

	return "\n".join(f"- {linie}" for linie in interpretari)


def afisare_descriere_variabila_text(variabila: str, descriere: dict):
	st.header(f"📝 `{variabila}` – variabilă text")
	
	stat = descriere.get("statistici", {})

	col1, col2 = st.columns(2)

	with col1:
		st.subheader("Statistici")
		if stat:
			st.markdown(f"- **Număr de valori**: {stat.get('count', 0)}")
			st.markdown(f"- **Valori unice**: {stat.get('nunique', 0)}")
		else:
			st.warning("Nu există statistici disponibile.")

		st.subheader("Top valori")
		top_valori = stat.get("top_valori", {})
		if top_valori:
			df_top = pd.DataFrame.from_dict(top_valori, orient="index", columns=["Frecvență"])
			df_top.index.name = "Valoare"
			st.dataframe(df_top.head(10), use_container_width=True)
		else:
			st.info("Nu există valori frecvente disponibile.")

	with col2:
		st.subheader("Interpretare")
		interpretare = descriere.get("interpretare", None)
		st.markdown(interpretare or "Interpretarea nu este disponibilă.")
