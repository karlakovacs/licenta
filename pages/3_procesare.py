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
	optiuni_individuale: dict = None,
) -> pd.DataFrame:
	df_copy = df.copy()

	if optiuni_individuale:
		# completare per coloana
		for col, opt in optiuni_individuale.items():
			df_copy[col] = fillna_coloana(
				df_copy[col],
				opt["strategie"],
				valoare_fixa=opt.get("valoare"),
			)
	else:
		# completare globala
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


def eliminare_varinata_mica(df: pd.DataFrame, threshold: float) -> tuple[pd.DataFrame, list[str]]:
	df_var = df.select_dtypes(include=TIPURI_NUMERICE)
	selector = VarianceThreshold(threshold=threshold)
	selector.fit(df_var)
	coloane_pastrate = df_var.columns[selector.get_support(indices=True)].tolist()
	coloane_eliminate = list(set(df_var.columns) - set(coloane_pastrate))
	restul = df.select_dtypes(exclude=TIPURI_NUMERICE)
	df_nou = pd.concat([df[coloane_pastrate], restul], axis=1)
	return df_nou, coloane_eliminate


def eliminare_corelate(df: pd.DataFrame, prag: float = 0.9) -> pd.DataFrame:
	corr_matrix = df.corr(numeric_only=True).abs()
	upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
	de_sters = [col for col in upper.columns if any(upper[col] > prag)]
	return df.drop(columns=de_sters), de_sters


def eliminare_coloane_cu_valori_lipsa(df: pd.DataFrame, prag_pct: int) -> tuple[pd.DataFrame, list]:
	pct_lipsa = df.isnull().mean() * 100
	coloane_de_sters = pct_lipsa[pct_lipsa > prag_pct].index.tolist()
	return df.drop(columns=coloane_de_sters), coloane_de_sters


def elimina_constante(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
	constante = [col for col in df.columns if df[col].nunique() == 1]
	return df.drop(columns=constante), constante


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


def selectare_caracteristici_catboost(X, y, num_features):
	cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
	model = CatBoostClassifier(verbose=0, random_state=42)
	model.fit(X, y, cat_features=cat_cols)

	feat_importance_df = model.get_feature_importance(prettified=True)
	top_features = feat_importance_df.nlargest(num_features, "Importances")
	X = X[top_features["Feature Id"].tolist()]
	return X, top_features


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


def ui_eliminare_randuri(df: pd.DataFrame):
	if st.checkbox("Șterge rânduri duplicate"):
		df, nr_duplicate = eliminare_duplicate(df)
		if nr_duplicate > 0:
			st.session_state["procesare"]["eliminare_duplicate"] = True
			st.success(f"{nr_duplicate} rânduri duplicate eliminate.")
		else:
			st.info("Nu există rânduri duplicate.")

	if st.checkbox("Elimină rândurile cu multe valori lipsă"):
		max_valori_lipsa = st.slider("Maxim valori lipsă per rând acceptate", 0, df.shape[1], 2)

		if st.button("Aplică", type="primary", key="randuri_nan"):
			df, nr_null_rows = eliminare_randuri_cu_valori_lipsa(df, max_valori_lipsa)

			if nr_null_rows > 0:
				st.session_state["procesare"]["eliminare_randuri_nan"] = {"max_valori_lipsa": max_valori_lipsa}
				st.success(f"{nr_null_rows} rânduri cu multe valori lipsă eliminate.")
			else:
				st.info("Niciun rând nu a fost eliminat pe baza valorilor lipsă.")

	return df


def ui_outlieri(df: pd.DataFrame):
	metoda_detectie = st.selectbox("Metodă de detecție", ["Z-score", "IQR"])
	actiune = st.radio("Acțiune asupra outlierilor", ["Eliminare", "Înlocuire cu NaN"])

	if st.button("Aplică", type="primary", key="outlieri"):
		df, coloane_modificate = tratare_outlieri(df, metoda=metoda_detectie, actiune=actiune)

		if coloane_modificate:
			st.session_state["procesare"]["outlieri"] = {"metoda_detectie": metoda_detectie, "actiune": actiune}
			st.success(f"Am detectat și tratat outlieri în coloanele: {', '.join(coloane_modificate)}")
		else:
			st.info("Nu au fost detectați outlieri în coloanele numerice.")
	return df


def ui_valori_lipsa_coloane(df: pd.DataFrame):
	if not df.isna().any().any():
		st.info("Nu există valori lipsă.")
		return df

	st.subheader("Alege cum vrei să completezi valorile lipsă:")
	mod_completare = st.radio(
		"Mod de completare",
		["Completare automată pe tipuri", "Completare personalizată per coloană"],
		horizontal=True,
	)

	if mod_completare == "Completare automată pe tipuri":
		strategie_num = st.selectbox("Strategie pentru numerice", ["medie", "mediana", "mod", "valoare fixă"])
		strategie_cat = st.selectbox("Strategie pentru categoriale", ["mod", "valoare fixă"])

		valoare_fixa_num = None
		valoare_fixa_cat = None

		if strategie_num == "valoare fixă":
			valoare_fixa_num = st.number_input("Valoare fixă pentru numerice")

		if strategie_cat == "valoare fixă":
			valoare_fixa_cat = st.text_input("Valoare fixă pentru categoriale")

		df = completare_valori_lipsa(
			df,
			strategie_num=strategie_num,
			strategie_cat=strategie_cat,
			valoare_fixa_num=valoare_fixa_num,
			valoare_fixa_cat=valoare_fixa_cat,
			optiuni_individuale=None,
		)
		st.session_state["procesare"]["valori_lipsa"] = {
			"mod": "automat",
			"strategie_numerice": strategie_num,
			"strategie_categoriale": strategie_cat,
			"valoare_fixa_numerice": valoare_fixa_num,
			"valoare_fixa_categoriale": valoare_fixa_cat,
		}

	else:
		st.header("Setează manual pentru fiecare coloană")
		optiuni_individuale = {}

		for col in df.columns[df.isnull().any()]:
			col_type = str(df[col].dtype)
			is_numeric = col_type in TIPURI_NUMERICE
			chei = ["medie", "mediana", "mod", "valoare fixă"] if is_numeric else ["mod", "valoare fixă"]

			with st.container():
				st.subheader(f"**`{col}` ({col_type})**")
				strategie = st.selectbox(f"Strategie pentru `{col}`", chei, key=f"{col}_strategie")

				val = None
				if strategie == "valoare fixă":
					if is_numeric:
						val = st.number_input(f"Valoare fixă pentru `{col}`", key=f"{col}_valoare")
					else:
						val = st.text_input(f"Valoare fixă pentru `{col}`", key=f"{col}_valoare")

				optiuni_individuale[col] = {
					"strategie": strategie,
					"valoare": val,
				}

		df = completare_valori_lipsa(df, optiuni_individuale=optiuni_individuale)
		st.session_state["procesare"]["valori_lipsa"] = {
			"mod": "individual",
			"strategie_per_coloana": optiuni_individuale,
		}

	st.success("Valorile lipsă au fost completate.")
	return df


def ui_coloane_binare(df: pd.DataFrame) -> pd.DataFrame:
	coloane_binare = [col for col in df.columns if df[col].nunique(dropna=True) == 2 and df[col].dtype != "bool"]

	if not coloane_binare:
		st.info("Nu există coloane binare ce necesită conversie.")
		return df

	st.markdown("Selectează valoarea care va fi considerată `True` pentru fiecare coloană binară:")
	conversii = {
		col: st.selectbox(f"`{col}` - valoarea `True`:", df[col].dropna().unique().tolist(), key=f"true_val_{col}")
		for col in coloane_binare
	}

	if st.button("Aplică", key="binar"):
		df = convertire_binar_in_bool(df, conversii)
		st.session_state["procesare"]["coloane_binare"] = {"conversii": conversii}
		st.success("Coloanele binare au fost convertite în `bool`.")

	return df


def ui_datetime(df: pd.DataFrame) -> pd.DataFrame:
	coloane_object = df.select_dtypes(include="object").columns.tolist()
	if not coloane_object:
		st.info("Nu există coloane de tip `object` care ar putea fi transformate în datetime.")
		return df

	coloane_datetime = st.multiselect("Alege coloane de tip datetime", coloane_object)

	if not coloane_datetime:
		return df

	datetime_format = st.text_input(
		"Formatul datetime (ex: `%Y-%m-%d %H:%M:%S`, `%d/%m/%Y`, etc.)",
		value="%Y-%m-%d",
	)

	componente = st.multiselect(
		"Componente de extras",
		["an", "luna", "zi", "ora", "minute", "zi_saptamana", "este_weekend"],
		default=["an", "luna", "zi"],
	)

	if st.button("Aplică", key="datetime"):
		df = procesare_datetime(df, coloane_datetime, datetime_format, componente)
		st.session_state["procesare"]["datetime"] = {
			"coloane": coloane_datetime,
			"format": datetime_format,
			"componente_extrase": componente,
		}
		st.success("Conversie și extragere de componente realizate.")

	return df


def ui_selectie_coloane(X: pd.DataFrame, y: pd.Series):
	# Eliminare manuală
	coloane_de_eliminat = st.multiselect("Alege coloanele de eliminat", X.columns, help="de ex id, nume")
	if coloane_de_eliminat and st.button("Aplică", type="primary", key="coloane_inutile"):
		X = drop_coloane_inutile(X, coloane_de_eliminat)
		st.session_state["procesare"]["eliminare_coloane_manual"] = coloane_de_eliminat
		st.success(f"Am eliminat coloanele: {', '.join(coloane_de_eliminat)}")

	# Variance Threshold
	if st.checkbox("Elimină coloane cu varianță mică"):
		threshold = st.slider("Prag pentru VarianceThreshold", 0.0, 1.0, 0.01, step=0.01)
		try:
			X, sterse = eliminare_varinata_mica(X, threshold)
			if sterse:
				st.session_state["procesare"]["varianta_mica"] = {"prag": threshold, "eliminate": sterse}
				st.success(f"Coloanele eliminate: {', '.join(sterse)}")
			else:
				st.info("Nicio coloană nu a fost eliminată — toate au varianță peste prag.")
		except Exception as e:
			st.error(f"Eroare: {e}")

	# Corelație
	if st.checkbox("Elimină coloane extrem de corelate"):
		X, eliminate = eliminare_corelate(X, prag=0.9)
		if eliminate:
			st.session_state["procesare"]["corelatii_mari"] = eliminate
			st.success(f"Coloanele eliminate (corelație > 0.9): {', '.join(eliminate)}")
		else:
			st.info("Nicio coloană nu a fost eliminată.")

	# Selectie CatBoost
	numar_coloane = st.slider(
		"Selectează numărul de caracteristici păstrate", min_value=1, max_value=X.shape[1], value=min(10, X.shape[1])
	)
	if st.button("Aplică", type="primary", key="selectie"):
		X, top_features = selectare_caracteristici_catboost(X, y, numar_coloane)

		st.session_state["procesare"]["selectie"] = {
			"numar_coloane": numar_coloane,
			"top_features": top_features["Feature Id"].tolist(),
		}

		fig = go.Figure()
		fig.add_trace(
			go.Bar(
				x=top_features["Importances"][::-1],
				y=top_features["Feature Id"][::-1],
				orientation="h",
				marker=dict(color="orange"),
			)
		)
		fig.update_layout(
			title="Importanța caracteristicilor (CatBoost)",
			xaxis_title="Importanță",
			yaxis_title="Caracteristică",
			margin=dict(l=80, r=20, t=50, b=50),
			height=400,
		)
		st.plotly_chart(fig, use_container_width=True)
		st.success("Am selectat automat cele mai importante caracteristici.")

	return X


# TODO: schimbat logica la label... aleg cele mai comune dupa value counts sau cum?
def ui_encoding(X: pd.DataFrame):
	coloane_categoriale = X.select_dtypes(include=["object", "category"]).columns.tolist()
	if not coloane_categoriale:
		st.info("Nu există coloane categoriale de procesat.")
		return X

	nr_max_categorii = st.slider("Max categorii per coloană", 2, 15, 10)

	st.subheader("Label Encoding")
	coloane_label = st.multiselect("Coloane pentru Label Encoding", coloane_categoriale - coloane_one_hot, key="coloane_label")

	label_mappings = {}
	for col in coloane_label:
		vals = X[col].dropna().unique().tolist()
		if len(vals) > nr_max_categorii:
			vals = vals[:nr_max_categorii]
		ordered = sort_items(vals)
		label_mappings[col] = ordered

	if label_mappings and st.button("Aplică Label Encoding", type="primary"):
		X = label_encoding(X, label_mappings)
		st.session_state["procesare"]["label_encoding"] = label_mappings
		st.success("Label Encoding aplicat.")

	st.divider()

	st.subheader("One-Hot Encoding")
	coloane_one_hot = st.multiselect("Coloane pentru One-Hot Encoding", coloane_categoriale - coloane_label, key="coloane_one_hot")

	if coloane_one_hot and st.button("Aplică One-Hot Encoding", type="primary"):
		X = one_hot_encoding(X, coloane_one_hot, nr_max_categorii)
		st.session_state["procesare"]["one_hot_encoding"] = {
			"coloane": coloane_one_hot,
			"max_categorii": nr_max_categorii,
		}
		st.success("One-Hot Encoding aplicat.")

	return X


def ui_dezechilibru(X: pd.DataFrame, y: pd.Series):
	optiune_dezechilibru = st.selectbox(
		"Strategia de gestionare a dezechilibrului dintre clase:",
		["Undersampling", "Oversampling", "ADASYN", "Niciuna"],
	)

	if st.button("Aplică", type="primary", key="dezechilibru"):
		X, y = gestionare_dezechilibru(X, y, optiune_dezechilibru)
		st.session_state["procesare"]["dezechilibru"] = {"strategie": optiune_dezechilibru}
		st.success("Dezechilibrul a fost tratat.")

	return X, y


def ui_scalare(X: pd.DataFrame):
	optiune_scalare = st.selectbox(
		"Alege metoda de scalare:", ["StandardScaler", "MinMaxScaler", "RobustScaler", "Niciuna"]
	)

	if st.button("Aplică", type="primary", key="scalare"):
		X = aplicare_scalare(X, optiune_scalare)
		st.success("Datele au fost scalate.")
		st.session_state["procesare"]["scalare"] = {"scaler": optiune_scalare}

	return X


def ui_impartire(X, y, tinta):
	proportie_test = st.slider(
		"Alege procentajul pentru setul de testare:",
		min_value=0.1,
		max_value=0.4,
		step=0.1,
		value=0.2,
	)
	stratificat = st.checkbox("Împărțire stratificată", value=True)

	if st.button("Aplică", type="primary", key="impartire"):
		X_train, X_test, y_train, y_test = impartire_train_test(X, y, tinta, proportie_test, stratificat)

		st.session_state["procesare"]["impartire"] = {
			"tinta": tinta,
			"proportie_test": proportie_test,
			"stratificat": stratificat,
		}

		st.success("Seturile de antrenare și testare au fost create.")

		for name, data in zip(["X_train", "X_test", "y_train", "y_test"], [X_train, X_test, y_train, y_test]):
			salvare_date_temp(data, name)
		st.success("Seturile au fost salvate.")


########################################################


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
		st.warning("Nasol")
		st.stop()

	st.header(set_date["denumire"])
	st.dataframe(df.head())

	with st.expander("🧹 Eliminarea rândurilor inutile (duplicate & valori lipsă)"):
		df = ui_eliminare_randuri(df)

	with st.expander("🔬 Detectarea și tratarea outlierilor"):
		df = ui_outlieri(df)

	with st.expander("🧩 Înlocuirea valorilor lipsă"):
		df = ui_valori_lipsa_coloane(df)

	with st.expander("🟢 Procesarea coloanelor binare"):
		df = ui_coloane_binare(df)

	with st.expander("📅 Procesarea coloanelor datetime"):
		df = ui_datetime(df)

	tinta = set_date["tinta"]
	X = df.drop(columns=[tinta])
	y = df[tinta]

	with st.expander("🖱️ Selecția coloanelor"):
		X = ui_selectie_coloane(X, y)

	with st.expander("🏷️ Encoding pentru coloanele categoriale"):
		X = ui_encoding(X)

	with st.expander("⚖️ Gestionarea dezechilibrului dintre clase"):
		X, y = ui_dezechilibru(X, y)

	with st.expander("📏 Scalarea datelor"):
		X = ui_scalare(X)

	with st.expander("🍰 Împărțirea în seturi de antrenare și testare"):
		ui_impartire(X, y, tinta)


if __name__ == "__main__":
	main()
