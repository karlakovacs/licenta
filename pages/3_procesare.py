from catboost import CatBoostClassifier
from imblearn.over_sampling import ADASYN, SMOTE
from imblearn.under_sampling import RandomUnderSampler
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
import streamlit as st
from streamlit_sortables import sort_items

from preprocessing import procesare_dataset
from utils import (
	TIPURI_CATEGORIALE,
	TIPURI_NUMERICE,
	citire_date_predefinite,
	citire_date_temp,
	nav_bar,
	salvare_date_temp,
)


st.set_page_config(layout="wide", page_title="Procesare", page_icon="🛠️")
nav_bar()


def procesare_datetime(
	df: pd.DataFrame,
	coloane_datetime: list[str],
	format: str = "%Y-%m-%d",
	componente: list[str] = ["an", "luna", "zi"],
) -> pd.DataFrame:
	for col in coloane_datetime:
		try:
			df[col] = pd.to_datetime(df[col], format=format)

			if "an" in componente:
				df[f"{col}_an"] = df[col].dt.year
			if "luna" in componente:
				df[f"{col}_luna"] = df[col].dt.month
			if "zi" in componente:
				df[f"{col}_zi"] = df[col].dt.day
			if "ora" in componente:
				df[f"{col}_ora"] = df[col].dt.hour
			if "minute" in componente:
				df[f"{col}_minute"] = df[col].dt.minute
			if "zi_saptamana" in componente:
				df[f"{col}_zi_saptamana"] = df[col].dt.weekday
			if "este_weekend" in componente:
				df[f"{col}_este_weekend"] = df[col].dt.weekday >= 5

		except Exception as e:
			st.error(f"Eroare la conversie pentru coloana `{col}`: {e}")

	return df


def fillna_coloana(col: pd.Series, strategie: str, valoare_fixa: any = None) -> pd.Series:
	if strategie == "medie":
		return col.fillna(col.mean())
	elif strategie == "mediana":
		return col.fillna(col.median())
	elif strategie == "mod":
		return col.fillna(col.mode().iloc[0])
	elif strategie == "valoare fixă":
		return col.fillna(valoare_fixa)
	else:
		return col


def completare_valori_lipsa(
	df: pd.DataFrame,
	strategie_num: str = "medie",
	strategie_cat: str = "mod",
	valoare_fixa_num: float = None,
	valoare_fixa_cat: str = None,
) -> pd.DataFrame:
	df_copy = df.copy()

	num_cols = df_copy.select_dtypes(include=TIPURI_NUMERICE).columns[
		df_copy.select_dtypes(include=TIPURI_NUMERICE).isnull().any()
	]
	cat_cols = df_copy.select_dtypes(include=TIPURI_CATEGORIALE).columns[
		df_copy.select_dtypes(include=TIPURI_CATEGORIALE).isnull().any()
	]

	for col in num_cols:
		df_copy[col] = fillna_coloana(df_copy[col], strategie_num, valoare_fixa_num)

	for col in cat_cols:
		df_copy[col] = fillna_coloana(df_copy[col], strategie_cat, valoare_fixa_cat)

	return df_copy


def convertire_binar_in_bool(df: pd.DataFrame, conversii: dict) -> pd.DataFrame:
	for col, true_val in conversii.items():
		df[col] = df[col].apply(lambda x: x == true_val)
	return df


def label_encoding(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
	for col, ordered_vals in mapping.items():
		df[col] = df[col].astype(pd.CategoricalDtype(categories=ordered_vals, ordered=True))  # .cat.codes
	return df


def one_hot_encoding(df: pd.DataFrame, coloane: list, nr_max_categorii: int = 10) -> pd.DataFrame:
	for col in coloane:
		if df[col].nunique() <= nr_max_categorii:
			dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=bool)
			df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
	return df


def drop_coloane_inutile(df: pd.DataFrame, coloane_de_eliminat: list[str]):
	df = df.drop(columns=coloane_de_eliminat)
	return df


def eliminare_coloane_cu_valori_lipsa(df: pd.DataFrame, prag_pct: int = 50) -> tuple[pd.DataFrame, list]:
	pct_lipsa = df.isnull().mean() * 100
	coloane_de_sters = pct_lipsa[pct_lipsa > prag_pct].index.tolist()
	return df.drop(columns=coloane_de_sters), coloane_de_sters



def detectare_outlieri_z_score(serie: pd.Series, threshold: float = 3.0) -> pd.Series:
	z_scores = (serie - serie.mean()) / serie.std()
	return z_scores.abs() > threshold


def detectare_outlieri_iqr(serie: pd.Series) -> pd.Series:
	Q1 = serie.quantile(0.25)
	Q3 = serie.quantile(0.75)
	IQR = Q3 - Q1
	return (serie < (Q1 - 1.5 * IQR)) | (serie > (Q3 + 1.5 * IQR))


def tratare_outlieri(
	df: pd.DataFrame, metoda: str = "Z-score", actiune: str = "Eliminare"
) -> tuple[pd.DataFrame, list[str]]:
	coloane_procesate = []
	df_copiat = df.copy()

	for col in df_copiat.select_dtypes(include=TIPURI_NUMERICE).columns:
		if metoda == "Z-score":
			conditie = detectare_outlieri_z_score(df_copiat[col])
		else:
			conditie = detectare_outlieri_iqr(df_copiat[col])

		if conditie.any():
			coloane_procesate.append(col)
			if actiune == "Eliminare":
				df_copiat = df_copiat[~conditie]
			else:
				df_copiat[col] = df_copiat[col].mask(conditie)

	return df_copiat, coloane_procesate


def eliminare_duplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
	nr_initial = df.shape[0]
	df_cleaned = df.drop_duplicates()
	nr_eliminate = nr_initial - df_cleaned.shape[0]
	return df_cleaned, nr_eliminate


def eliminare_randuri_cu_valori_lipsa(df: pd.DataFrame, max_valori_lipsa: int) -> tuple[pd.DataFrame, int]:
	nr_initial = df.shape[0]
	mask = df.isnull().sum(axis=1) <= max_valori_lipsa
	df_cleaned = df[mask]
	nr_eliminate = nr_initial - df_cleaned.shape[0]
	return df_cleaned, nr_eliminate



def gestionare_dezechilibru(X, y, strategie):
	if strategie == "Undersampling":
		X, y = RandomUnderSampler(sampling_strategy="majority", random_state=42).fit_resample(X, y)
	elif strategie == "Oversampling":
		X, y = SMOTE(sampling_strategy="minority", random_state=42).fit_resample(X, y)
	elif strategie == "ADASYN":
		X, y = ADASYN(sampling_strategy="minority", random_state=42).fit_resample(X, y)
	return X, y


def aplicare_scalare(X, metoda):
	scaler = None
	if metoda == "StandardScaler":
		scaler = StandardScaler()
	elif metoda == "MinMaxScaler":
		scaler = MinMaxScaler()
	elif metoda == "RobustScaler":
		scaler = RobustScaler()
	if scaler:
		# Selectează doar coloanele numerice "pure"
		coloane_numerice = X.select_dtypes(exclude=["category", "object", "bool"]).columns.tolist()
		# Scalăm doar acele coloane
		X_scaled = pd.DataFrame(scaler.fit_transform(X[coloane_numerice]), columns=coloane_numerice, index=X.index)
		# Restul coloanelor rămân nemodificate
		X_rest = X.drop(columns=coloane_numerice)
		# Concatenăm și păstrăm ordinea originală
		X = pd.concat([X_scaled, X_rest], axis=1)
		X = X[X.columns.tolist()]  # păstrează ordinea exact cum era

	return X


def impartire_train_test(X: pd.DataFrame, y: pd.Series, coloana_tinta: str, proportie_test: float, stratificat: bool):
	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=proportie_test,
		stratify=y if stratificat else None,
		random_state=42,
	)

	X_train = pd.DataFrame(X_train, columns=X.columns).reset_index(drop=True)
	X_test = pd.DataFrame(X_test, columns=X.columns).reset_index(drop=True)
	y_train = pd.Series(y_train, name=coloana_tinta).reset_index(drop=True)
	y_test = pd.Series(y_test, name=coloana_tinta).reset_index(drop=True)

	return X_train, X_test, y_train, y_test


######################## UI #########################


def ui_eliminare_coloane(df: pd.DataFrame):
	st.session_state["procesare"].setdefault("coloane_eliminate", [])

	coloane_eliminate = st.multiselect(
		"Alege coloanele de eliminat",
		options=df.columns,
		# default=st.session_state["procesare"]["coloane_eliminate"],
		help="Coloane care nu aduc valoare, cum ar fi ID-uri, coduri, etc.",
		key="coloane_eliminate",
	)

	if coloane_eliminate:
		st.session_state["procesare"]["coloane_eliminate"] = coloane_eliminate


def ui_eliminare_randuri(df: pd.DataFrame):
	are_duplicate = df.duplicated().any()
	are_nan = df.isnull().any().any()

	if are_duplicate:
		elim_dup = st.checkbox(
			"Șterge rânduri duplicate",
			# value=st.session_state["procesare"].get("eliminare_duplicate", False),
			help="Elimină rândurile complet duplicate, dacă există.",
			key="elim_dup",
		)
		if elim_dup:
			st.session_state["procesare"]["eliminare_duplicate"] = True
		else:
			st.session_state["procesare"].pop("eliminare_duplicate", None)
	else:
		st.info("Setul de date nu conține rânduri duplicate.")

	if are_nan:
		elim_nan = st.checkbox(
			"Elimină rânduri cu peste 50% valori lipsă",
			value=st.session_state["procesare"].get("eliminare_randuri_nan", False),
			help="Elimină rândurile care au prea multe valori lipsă.",
		)
		if elim_nan:
			st.session_state["procesare"]["eliminare_randuri_nan"] = True
		else:
			st.session_state["procesare"].pop("eliminare_randuri_nan", None)
	else:
		st.info("Nu există valori lipsă în setul de date.")


def ui_outlieri(df: pd.DataFrame):
	metoda_detectie = st.radio(
		"Metodă de detecție",
		["Z-score", "IQR"],
		index=0,
		help="Alege cum sunt detectați outlierii: Z-score detectează valori extreme pe baza deviației standard, iar IQR pe baza intervalului intercuartilic.",
	)
	actiune = st.radio(
		"Acțiune asupra outlierilor",
		["Eliminare", "Înlocuire cu NaN"],
		index=0,
		help="Poți fie să elimini complet observațiile cu outlieri, fie să înlocuiești valorile extreme cu NaN.",
	)

	st.session_state["procesare"]["outlieri"] = {
		"metoda": metoda_detectie,
		"actiune": actiune,
	}


def ui_valori_lipsa_coloane(df: pd.DataFrame):
	are_nan = df.isnull().any().any()
	if are_nan:
		strategie_numerice = st.selectbox(
			"Strategie pentru variabilele numerice",
			["medie", "mediană", "mod", "valoare fixă"],
			help="Alege cum să completezi valorile lipsă din coloanele numerice.",
		)

		strategie_categoriale = st.selectbox(
			"Strategie pentru variabilele categoriale",
			["mod", "valoare fixă"],
			help="Alege cum să completezi valorile lipsă din coloanele categoriale.",
		)

		valoare_fixa_numerice = None
		valoare_fixa_categoriale = None

		if strategie_numerice == "valoare fixă":
			valoare_fixa_numerice = st.number_input(
				"Valoare fixă pentru variabilele numerice", help="Valoare numerică fixă folosită la completare."
			)

		if strategie_categoriale == "valoare fixă":
			valoare_fixa_categoriale = st.text_input(
				"Valoare fixă pentru variabilele categoriale", help="Valoare textuală fixă folosită la completare."
			)

		st.session_state["procesare"]["valori_lipsa"] = {
			"strategie_numerice": strategie_numerice,
			"strategie_categoriale": strategie_categoriale,
			"valoare_fixa_numerice": valoare_fixa_numerice,
			"valoare_fixa_categoriale": valoare_fixa_categoriale,
		}
	else:
		st.info("Nu există valori lipsă în setul de date.")


def ui_coloane_binare(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state["procesare"].get("coloane_eliminate", []))

	coloane_binare = [
		col
		for col in df.columns
		if col not in coloane_eliminate and df[col].nunique(dropna=True) == 2 and df[col].dtype != "bool"
	]

	if not coloane_binare:
		st.info("Nu există coloane binare ce necesită conversie.")
		return

	st.markdown("Selectează valoarea care va fi considerată `True` pentru fiecare coloană binară:")

	conversii_initiale = st.session_state["procesare"].get("coloane_binare", {})
	conversii = {}
	for col in coloane_binare:
		valori_unice = df[col].dropna().unique().tolist()
		conversii[col] = st.selectbox(
			f"`{col}`",
			options=valori_unice,
			index=valori_unice.index(conversii_initiale.get(col, valori_unice[0])),
			key=f"true_val_{col}",
			help=f"Alege care valoare din `{valori_unice}` va deveni `True`.",
		)
	st.session_state["procesare"]["coloane_binare"] = conversii


def ui_datetime(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state["procesare"].get("coloane_eliminate", []))

	coloane_object = list(set(df.select_dtypes(include="object").columns) - coloane_eliminate)

	if not coloane_object:
		st.info("Nu există coloane de tip `object` care ar putea fi transformate în datetime.")
		return

	coloane_datetime = st.multiselect(
		"Alege coloane de tip datetime",
		coloane_object,
		default=st.session_state["procesare"]["datetime"].get("coloane", []),
	)

	datetime_format = st.text_input(
		"Formatul datetime (ex: `%Y-%m-%d %H:%M:%S`, `%d/%m/%Y`, etc.)",
		value=st.session_state["procesare"]["datetime"].get("format", "%Y-%m-%d"),
	)

	componente = st.multiselect(
		"Componente de extras",
		["an", "luna", "zi", "ora", "minute", "zi_saptamana", "este_weekend"],
		default=st.session_state["procesare"]["datetime"].get("componente_extrase", ["an", "luna", "zi"]),
	)

	st.session_state["procesare"]["datetime"] = {
		"coloane": coloane_datetime,
		"format": datetime_format,
		"componente_extrase": componente,
	}


def ui_encoding(df: pd.DataFrame):
	coloane_eliminate = set(st.session_state["procesare"].get("coloane_eliminate", []))
	coloane_datetime = set(st.session_state["procesare"].get("datetime", {}).get("coloane", []))
	coloane_categoriale = list(
		set(df.select_dtypes(include=["object", "category"]).columns) - coloane_eliminate - coloane_datetime
	)

	if not coloane_categoriale:
		st.info("Nu există coloane categoriale de procesat.")
		return

	nr_max_categorii = st.slider("Max categorii per coloană", 2, 15, 10)

	st.subheader("Label Encoding")
	coloane_label = st.multiselect("Coloane pentru Label Encoding", coloane_categoriale, key="coloane_label")

	label_mappings = {}
	for col in coloane_label:
		vals = df[col].dropna().unique().tolist()
		if len(vals) > nr_max_categorii:
			vals = df[col].dropna().value_counts().index.tolist()[:nr_max_categorii]
		ordered = sort_items(vals)
		label_mappings[col] = ordered

	st.divider()

	st.subheader("One-Hot Encoding")
	coloane_one_hot = st.multiselect("Coloane pentru One-Hot Encoding", coloane_categoriale, key="coloane_one_hot")

	st.session_state["procesare"]["encoding"] = {
		"max_categorii": nr_max_categorii,
		"label_encoding": label_mappings,
		"one_hot_encoding": coloane_one_hot,
	}


def ui_dezechilibru():
	optiune_dezechilibru = st.selectbox(
		"Strategia de gestionare a dezechilibrului dintre clase:",
		["Undersampling", "Oversampling", "ADASYN", "Niciuna"],
		key="dezechilibru",
	)
	st.session_state["procesare"]["dezechilibru"] = optiune_dezechilibru


def ui_scalare():
	optiune_scalare = st.selectbox(
		"Alege metoda de scalare:", ["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"], key="scalare"
	)
	st.session_state["procesare"]["scalare"] = optiune_scalare


def ui_impartire():
	impartire_existenta = st.session_state["procesare"].get("impartire", {})

	proportie_test = st.slider(
		"Alege procentajul pentru setul de testare:",
		min_value=0.1,
		max_value=0.4,
		step=0.1,
		value=impartire_existenta.get("proportie_test", 0.2),
		key="impartire_proportie_test",
	)

	stratificat = st.checkbox(
		"Împărțire stratificată",
		value=impartire_existenta.get("stratificat", True),
		key="impartire_stratificat",
	)

	st.session_state["procesare"]["impartire"] = {
		"proportie_test": proportie_test,
		"stratificat": stratificat,
	}


def main():
	st.title("Procesarea datelor")

	set_date: dict = st.session_state.get("set_date", None)
	df: pd.DataFrame = None
	st.session_state.setdefault("procesare", {})

	if set_date["sursa"] != "predefinit":
		df = citire_date_temp(set_date["denumire"])
	else:
		df = citire_date_predefinite(set_date["denumire"])

	if df is None:
		st.error("Setul de date nu a putut fi încărcat")
		st.stop()

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

	st.write(st.session_state["set_date"])
	st.write(st.session_state["procesare"])

	if st.button("Aplică toți pașii de procesare", type="primary"):
		st.success("Preprocesarea a fost aplicată cu succes!")
		st.dataframe(df.head())

	# for name, data in zip(["X_train", "X_test", "y_train", "y_test"], [X_train, X_test, y_train, y_test]):
	# 	salvare_date_temp(data, name)
	# st.success("Seturile au fost salvate.")


if __name__ == "__main__":
	main()
