import pandas as pd
import streamlit as st

from dataset import citire_date_predefinite, citire_date_temp
from preprocessing import procesare_dataset
from utils import nav_bar


st.set_page_config(layout="wide", page_title="FlagML | Procesare", page_icon="assets/logo.png")
nav_bar()


def ui_eliminare_coloane(df: pd.DataFrame):
	st.multiselect(
		"Alege coloanele de eliminat",
		options=df.columns,
		help="Coloane care nu aduc valoare, cum ar fi ID-uri, coduri, etc.",
		key="coloane_eliminate",
	)


def ui_eliminare_randuri(df: pd.DataFrame):
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


def ui_outlieri(df: pd.DataFrame):
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


def ui_valori_lipsa_coloane(df: pd.DataFrame):
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


def ui_coloane_binare(df: pd.DataFrame):
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


def ui_datetime(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state.get("coloane_eliminate", []))
	coloane_object_raw = set(df.select_dtypes(include=["object", "category"]).columns)
	coloane_object = list(coloane_object_raw - coloane_eliminate)

	if not coloane_object:
		st.info("Nu există coloane de tip `object` care ar putea fi transformate în datetime.")
		return

	st.multiselect(
		"Alege coloane de tip datetime",
		options=coloane_object,
		key="datetime_coloane",
	)

	st.text_input(
		"Formatul datetime (ex: `%Y-%m-%d %H:%M:%S`, `%d/%m/%Y`, etc.)",
		key="datetime_format",
	)

	st.multiselect(
		"Componente de extras",
		options=["an", "luna", "zi", "ora", "minute", "zi_saptamana", "este_weekend"],
		key="datetime_componente",
	)


def ui_encoding(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state.get("coloane_eliminate", []))
	coloane_binare = set(st.session_state.get("coloane_binare", []))
	coloane_datetime = set(st.session_state.get("datetime_coloane", []))
	coloane_categoriale_raw = set(df.select_dtypes(include=["object", "category"]).columns)
	coloane_categoriale = list(coloane_categoriale_raw - coloane_eliminate - coloane_datetime)

	if not coloane_categoriale:
		st.info("Nu există coloane categoriale de procesat.")
	else:
		encoding_dorit = st.checkbox(
			"Aplică encoding variabilelor categoriale",
			key="encoding_dorit",
			help="Toate variabilele categorice vor fi encodate automat folosind one-hot encoding, cu excepția celor specificate la `Label Encoding`.",
		)
		if encoding_dorit:
			st.slider("Max categorii per coloană", 2, 15, 10, key="encoding_max_categorii")
			st.multiselect("Coloane pentru Label Encoding", options=coloane_categoriale, key="encoding_coloane_label")


def ui_dezechilibru():
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


def ui_scalare():
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


def ui_impartire():
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
			"format": st.session_state.get("datetime_format", "%Y-%m-%d"),
			"componente": st.session_state.get("datetime_componente", []),
		}

	if st.session_state.get("encoding_dorit"):
		procesare["encoding"] = {
			"max_categorii": st.session_state.get("encoding_max_categorii", 10),
			"coloane_label": st.session_state.get("encoding_coloane_label", []),
			# "coloane_one_hot": st.session_state.get("encoding_coloane_one_hot", []),
		}

	procesare["dezechilibru"] = st.session_state.get("dezechilibru", "Niciuna")

	procesare["scalare"] = st.session_state.get("scalare", "Niciuna")

	procesare["impartire"] = {
		"proportie_test": st.session_state.get("impartire_proportie_test", 0.2),
		"stratificat": st.session_state.get("impartire_stratificat", True),
		"tinta": st.session_state["set_date"].get("tinta", None),
	}

	st.session_state["procesare"] = procesare


st.title("Procesarea datelor")

set_date: dict = st.session_state.get("set_date", None)
df: pd.DataFrame = None

if set_date is None:
	st.warning("Alegeți un set de date mai întâi.")

else:
	if set_date["sursa"] != "Seturi predefinite":
		df = citire_date_temp(set_date["denumire"])
	else:
		df = citire_date_predefinite(set_date["denumire"])

	if df is None:
		st.error("Setul de date nu a putut fi încărcat")

	else:
		st.header(set_date["denumire"])
		st.dataframe(df.head())

		with st.expander("🧹 Eliminarea coloanelor inutile"):
			ui_eliminare_coloane(df)

		with st.expander("🧹 Eliminarea rândurilor inutile (duplicate & valori lipsă)"):
			ui_eliminare_randuri(df)

		with st.expander("🔬 Detectarea și tratarea outlierilor"):
			ui_outlieri(df)

		with st.expander("🧩 Înlocuirea valorilor lipsă"):
			ui_valori_lipsa_coloane(df)

		with st.expander("🟢 Procesarea coloanelor binare"):
			ui_coloane_binare(df)

		with st.expander("📅 Procesarea coloanelor datetime"):
			ui_datetime(df)

		with st.expander("🏷️ Encoding pentru coloanele categoriale"):
			ui_encoding(df)

		with st.expander("⚖️ Gestionarea dezechilibrului dintre clase"):
			ui_dezechilibru()

		with st.expander("📏 Scalarea datelor"):
			ui_scalare()

		with st.expander("🍰 Împărțirea în seturi de antrenare și testare"):
			ui_impartire()

		if st.button("Procesare", type="primary", disabled="procesare_realizata" in st.session_state):
			creare_dict_procesare()
			# st.json(st.session_state["procesare"])
			procesare_dataset(df, st.session_state["procesare"])
			st.session_state.procesare_realizata = True
			st.session_state.get("pagini").update({4: True})
			# st.rerun()
			st.toast("Preprocesarea a fost aplicată cu succes!", icon="✅")
