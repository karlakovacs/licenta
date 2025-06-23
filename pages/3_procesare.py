import pandas as pd
import streamlit as st
from streamlit_sortables import sort_items

from database import create_set_date_procesat
from dataset import citire_set_date
from preprocessing import procesare_dataset
from ui import *


initializare_pagina("FlagML", "centered", "Procesarea datelor")


def sectiune_eliminare_coloane(df: pd.DataFrame):
	st.session_state.setdefault(
		"coloane_irelevante",
		[
			col
			for col in df.columns
			if df[col].nunique() > 15
			and (pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]))
			and not pd.api.types.is_float_dtype(df[col])
		],
	)

	st.multiselect(
		"Alege coloanele de eliminat",
		options=df.columns,
		default=st.session_state.coloane_irelevante,
		help="Coloane care nu aduc valoare, cum ar fi ID-uri, coduri, etc.",
		key="coloane_eliminate",
	)


def sectiune_eliminare_randuri(df: pd.DataFrame):
	are_duplicate = df.duplicated().any()
	are_nan = df.isnull().any().any()

	if are_duplicate:
		st.checkbox(
			"Șterge rândurile duplicate",
			help="Elimină rândurile complet duplicate, dacă există.",
			key="eliminare_duplicate",
		)
	else:
		st.info("Setul de date nu conține rânduri duplicate.")

	if are_nan:
		st.checkbox(
			"Elimină rândurile cu peste 50% valori lipsă",
			help="Elimină rândurile care au prea multe valori lipsă.",
			key="eliminare_randuri_nan",
		)
	else:
		st.info("Nu există valori lipsă în setul de date.")


def sectiune_outlieri(df: pd.DataFrame):
	tinta = st.session_state["set_date"]["tinta"]
	coloane_numerice = df.drop(columns=[tinta]).select_dtypes(include=["number"]).columns

	if len(coloane_numerice) == 0:
		st.info("Setul de date nu conține coloane numerice care pot fi analizate pentru outlieri.")
		return

	eliminare_outlieri = st.checkbox(
		"Aplică procesarea outlierilor",
		help="Activează acest pas pentru a detecta și elimina valorile extreme din setul de date.",
		key="eliminare_outlieri",
	)

	if eliminare_outlieri:
		st.radio(
			"Metodă de detecție",
			["Z-score", "IQR"],
			index=0,
			help="Alege cum sunt detectați outlierii: Z-score detectează valori extreme pe baza deviației standard, iar IQR pe baza intervalului intercuartilic.",
			key="outlieri_detectie",
		)
		st.radio(
			"Acțiune asupra outlierilor",
			["Eliminare", "Înlocuire cu NaN"],
			index=0,
			help="Poți fie să elimini complet observațiile cu outlieri, fie să înlocuiești valorile extreme cu NaN.",
			key="outlieri_actiune",
		)


def sectiune_valori_lipsa_coloane(df: pd.DataFrame):
	are_nan = df.isnull().any().any()
	if are_nan:
		strategie_numerice = st.selectbox(
			"Strategie pentru variabilele numerice",
			["medie", "mediană", "mod", "valoare fixă"],
			help="Alege cum să completezi valorile lipsă din coloanele numerice.",
			key="strategie_numerice",
		)

		strategie_categoriale = st.selectbox(
			"Strategie pentru variabilele categoriale",
			["mod", "valoare fixă"],
			help="Alege cum să completezi valorile lipsă din coloanele categoriale.",
			key="strategie_categoriale",
		)

		if strategie_numerice == "valoare fixă":
			st.number_input(
				"Valoare fixă pentru variabilele numerice",
				help="Valoare numerică fixă folosită la completare.",
				key="valoare_fixa_numerice",
			)

		if strategie_categoriale == "valoare fixă":
			st.text_input(
				"Valoare fixă pentru variabilele categoriale",
				help="Valoare textuală fixă folosită la completare.",
				key="valoare_fixa_categoriale",
			)
	else:
		st.info("Nu există valori lipsă în setul de date.")


def sectiune_coloane_binare(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state.get("coloane_eliminate", []))

	if "coloane_binare" not in st.session_state:
		coloane_binare = [
			col
			for col in df.columns
			if col not in coloane_eliminate and df[col].nunique(dropna=True) == 2 and df[col].dtype != "bool"
		]
		st.session_state["coloane_binare"] = coloane_binare

	coloane_binare = st.session_state.get("coloane_binare", None)

	if not coloane_binare:
		st.info("Nu există coloane binare ce necesită conversie.")
		return

	st.markdown("Selectează valoarea care va fi considerată `True` pentru fiecare coloană binară:")

	conversii = {}
	for col in coloane_binare:
		valori_unice = df[col].dropna().unique().tolist()
		conversii[col] = st.selectbox(
			f"`{col}`",
			options=valori_unice,
			key=f"binar_valoare_true_{col}",
			help=f"Alege care valoare va deveni `True`.",
		)


def sectiune_datetime(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state.get("coloane_eliminate", []))
	coloane_datetime_raw = df.select_dtypes(include=["datetime"]).columns
	coloane_datetime = [col for col in coloane_datetime_raw if col not in coloane_eliminate]

	if not coloane_datetime:
		st.info("Nu există coloane de tip `datetime`.")
		return

	st.multiselect(
		"Alege coloane de tip datetime",
		options=coloane_datetime,
		key="datetime_coloane",
	)

	st.multiselect(
		"Componente de extras",
		options=["an", "luna", "zi", "ora", "minute", "zi_saptamana", "este_weekend"],
		key="datetime_componente",
	)


def sectiune_encoding(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state.get("coloane_eliminate", []))
	coloane_binare = set(st.session_state.get("coloane_binare", []))
	coloane_datetime = set(st.session_state.get("datetime_coloane", []))
	coloane_categoriale_raw = set(df.select_dtypes(include=["object", "category"]).columns)
	coloane_categoriale = list(coloane_categoriale_raw - coloane_eliminate - coloane_datetime - coloane_binare)

	if not coloane_categoriale:
		st.info("Nu există coloane categoriale de procesat.")
	else:
		encoding_dorit = st.checkbox(
			"Aplică encoding variabilelor categoriale",
			key="encoding_dorit",
			help="Toate variabilele categorice vor fi encodate automat folosind one-hot encoding (salvându-se primele 10 valori unice), cu excepția celor specificate la `Label Encoding`.",
		)
		if encoding_dorit:
			encoding_coloane_label = st.multiselect(
				"Coloane pentru Label Encoding", options=coloane_categoriale, key="encoding_coloane_label"
			)

			st.session_state.setdefault("label_ordine_sortare", {})

			for col in encoding_coloane_label:
				st.markdown(f"Sortează valorile din coloana **{col}** în ordinea dorită:")
				unique_values = [str(v) for v in df[col].dropna().unique().tolist()]
				sorted_values = sort_items(unique_values, direction="horizontal", key=f"sort_{col}")
				st.markdown(f"Ordine aleasă: `{sorted_values}`")
				st.session_state["label_ordine_sortare"][col] = sorted_values


def sectiune_dezechilibru():
	st.selectbox(
		"Strategia de gestionare a dezechilibrului dintre clase:",
		["Undersampling", "Oversampling", "ADASYN", "Niciuna"],
		key="dezechilibru",
		help="""
			Alege o metodă pentru a corecta dezechilibrul dintre clase:
			- `Undersampling` reduce clasa majoritară;
			- `Oversampling` mărește clasa minoritară;
			- `ADASYN` creează exemple sintetice.
			Selectează `Niciuna` pentru a nu aplica nimic.
			""",
	)


def sectiune_scalare():
	st.selectbox(
		"Alege metoda de scalare:",
		["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"],
		key="scalare",
		help="""
			- `StandardScaler` elimină media și normalizează deviația standard.
			- `MinMaxScaler` aduce toate valorile în intervalul [0, 1].
			- `RobustScaler` este rezistent la outlieri.
			Alege `Niciuna` dacă nu vrei să aplici scalare.
		""",
	)


def sectiune_impartire():
	st.slider(
		"Alege procentajul pentru setul de testare:",
		min_value=0.1,
		max_value=0.4,
		step=0.1,
		value=0.2,
		key="impartire_proportie_test",
		help="Procent din setul de date folosit pentru testare. Restul va fi pentru antrenare.",
	)

	st.checkbox(
		"Împărțire stratificată",
		key="impartire_stratificat",
		help="Menține proporția claselor în ambele seturi de antrenare și testare.",
	)


def creare_dict_procesare():
	procesare = {}

	procesare["coloane_eliminate"] = st.session_state.get("coloane_eliminate", [])

	if st.session_state.get("eliminare_duplicate"):
		procesare["eliminare_duplicate"] = True
	if st.session_state.get("eliminare_randuri_nan"):
		procesare["eliminare_randuri_nan"] = True

	if st.session_state.get("eliminare_outlieri"):
		procesare["outlieri"] = {
			"detectie": st.session_state.get("outlieri_detectie"),
			"actiune": st.session_state.get("outlieri_actiune"),
		}

	if "strategie_numerice" in st.session_state or "strategie_categoriale" in st.session_state:
		procesare["valori_lipsa"] = {
			"strategie_numerice": st.session_state.get("strategie_numerice"),
			"valoare_fixa_numerice": st.session_state.get("valoare_fixa_numerice"),
			"strategie_categoriale": st.session_state.get("strategie_categoriale"),
			"valoare_fixa_categoriale": st.session_state.get("valoare_fixa_categoriale"),
		}

	conversii = {
		k.replace("binar_valoare_true_", ""): v
		for k, v in st.session_state.items()
		if k.startswith("binar_valoare_true_")
	}
	if conversii:
		procesare["coloane_binare"] = conversii

	if st.session_state.get("datetime_coloane"):
		procesare["datetime"] = {
			"coloane": st.session_state.get("datetime_coloane", []),
			"componente": st.session_state.get("datetime_componente", []),
		}

	if st.session_state.get("encoding_dorit"):
		procesare["encoding"] = {
			"max_categorii": 10,
			"coloane_label": st.session_state.get("label_ordine_sortare", {}),
		}

	procesare["dezechilibru"] = st.session_state.get("dezechilibru", "Niciuna")

	procesare["scalare"] = st.session_state.get("scalare", "Niciuna")

	procesare["impartire"] = {
		"proportie_test": st.session_state.get("impartire_proportie_test", 0.2),
		"stratificat": st.session_state.get("impartire_stratificat", True),
		"tinta": st.session_state["set_date"].get("tinta", None),
	}

	st.session_state["procesare"] = procesare


@require_auth
@require_selected_dataset
def main():
	set_date: dict = st.session_state.get("set_date", None)
	df: pd.DataFrame = citire_set_date(set_date)

	st.header(set_date["denumire"])
	st.dataframe(df.head())

	with st.expander("🧹 Eliminarea coloanelor inutile"):
		sectiune_eliminare_coloane(df)

	with st.expander("🧹 Eliminarea rândurilor inutile (duplicate & valori lipsă)"):
		sectiune_eliminare_randuri(df)

	with st.expander("🔬 Detectarea și tratarea outlierilor"):
		sectiune_outlieri(df)

	with st.expander("🧩 Înlocuirea valorilor lipsă"):
		sectiune_valori_lipsa_coloane(df)

	with st.expander("🟢 Procesarea coloanelor binare"):
		sectiune_coloane_binare(df)

	with st.expander("📅 Procesarea coloanelor datetime"):
		sectiune_datetime(df)

	with st.expander("🏷️ Encoding pentru coloanele categoriale"):
		sectiune_encoding(df)

	with st.expander("⚖️ Gestionarea dezechilibrului dintre clase"):
		sectiune_dezechilibru()

	with st.expander("📏 Scalarea datelor"):
		sectiune_scalare()

	with st.expander("🍰 Împărțirea în seturi de antrenare și testare"):
		sectiune_impartire()

	if st.button("Procesare", type="primary", disabled=verificare_flag("processed_dataset")):
		creare_dict_procesare()
		# st.json(st.session_state["procesare"])
		df = procesare_dataset(df, st.session_state["procesare"])
		st.session_state.id_set_procesat = create_set_date_procesat(
			st.session_state.get("id_utilizator"),
			st.session_state.get("id_set_date", 1),
			st.session_state.get("procesare"),
			df,
		)
		setare_flag("processed_dataset")
		st.toast("Preprocesarea a fost aplicată cu succes!", icon="✅")


if __name__ == "__main__":
	main()
