from imblearn.over_sampling import ADASYN, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, OneHotEncoder, RobustScaler, StandardScaler

from database import *
from utils import *


def eliminare_coloane(df: pd.DataFrame, coloane: list) -> pd.DataFrame:
	return df.drop(columns=coloane, errors="ignore")


def eliminare_duplicate(df: pd.DataFrame) -> pd.DataFrame:
	return df.drop_duplicates()


def eliminare_randuri_nan(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
	max_na = int(df.shape[1] * threshold)
	return df[df.isnull().sum(axis=1) <= max_na]


def tratare_outlieri(df: pd.DataFrame, metoda: str, actiune: str) -> pd.DataFrame:
	numerice = df.select_dtypes(include="number").columns
	df_nou = df.copy()
	for col in numerice:
		if metoda == "Z-score":
			z_scores = (df[col] - df[col].mean()) / df[col].std()
			mask = z_scores.abs() > 3
		elif metoda == "IQR":
			Q1 = df[col].quantile(0.25)
			Q3 = df[col].quantile(0.75)
			IQR = Q3 - Q1
			mask = (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)
		else:
			continue

		if actiune == "Eliminare":
			df_nou = df_nou[~mask]
		elif actiune == "Înlocuire cu NaN":
			df_nou.loc[mask, col] = pd.NA

	return df_nou


def completare_valori_lipsa(df: pd.DataFrame, setari: dict) -> pd.DataFrame:
	df_nou = df.copy()
	for col in df.columns:
		if df[col].isnull().any():
			if df[col].dtype in ["float64", "int64"]:
				s = setari.get("strategie_numerice")
				if s == "medie":
					df_nou[col].fillna(df[col].mean(), inplace=True)
				elif s == "mediană":
					df_nou[col].fillna(df[col].median(), inplace=True)
				elif s == "mod":
					df_nou[col].fillna(df[col].mode()[0], inplace=True)
				elif s == "valoare fixă":
					df_nou[col].fillna(setari.get("valoare_fixa_numerice"), inplace=True)
			else:
				s = setari.get("strategie_categoriale")
				if s == "mod":
					df_nou[col].fillna(df[col].mode()[0], inplace=True)
				elif s == "valoare fixă":
					df_nou[col].fillna(setari.get("valoare_fixa_categoriale"), inplace=True)
	return df_nou


def conversie_coloane_binare(df: pd.DataFrame, conversii: dict) -> pd.DataFrame:
	for col, true_val in conversii.items():
		df[col] = df[col] == true_val
	return df


def aplicare_datetime(df: pd.DataFrame, setari: dict) -> pd.DataFrame:
	for col in setari["coloane"]:
		df[col] = pd.to_datetime(df[col], format=setari["format"], errors="coerce")
		if "an" in setari["componente"]:
			df[f"{col}_an"] = df[col].dt.year
		if "luna" in setari["componente"]:
			df[f"{col}_luna"] = df[col].dt.month
		if "zi" in setari["componente"]:
			df[f"{col}_zi"] = df[col].dt.day
		if "ora" in setari["componente"]:
			df[f"{col}_ora"] = df[col].dt.hour
		if "minute" in setari["componente"]:
			df[f"{col}_minute"] = df[col].dt.minute
		if "zi_saptamana" in setari["componente"]:
			df[f"{col}_zi_saptamana"] = df[col].dt.weekday
		if "este_weekend" in setari["componente"]:
			df[f"{col}_este_weekend"] = df[col].dt.weekday >= 5
		df.drop(columns=col, inplace=True)
	return df


def aplicare_encoding(df: pd.DataFrame, setari: dict) -> pd.DataFrame:
	max_categorii = setari.get("max_categorii", 10)
	coloane_label = setari.get("coloane_label", [])

	df = df.copy()

	for col in coloane_label:
		encoder = LabelEncoder()
		df[col] = encoder.fit_transform(df[col].astype(str))

	potentiale_categorice = df.select_dtypes(include=["object", "category"]).columns.tolist()
	coloane_one_hot = [col for col in potentiale_categorice if col not in coloane_label]

	if coloane_one_hot:
		encoder = OneHotEncoder(
			drop="first", max_categories=max_categorii, sparse_output=False, handle_unknown="ignore"
		)
		encoded = encoder.fit_transform(df[coloane_one_hot].astype(str))
		encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(coloane_one_hot), index=df.index)

		df = df.drop(columns=coloane_one_hot)
		df = pd.concat([df, encoded_df], axis=1)

	return df


def aplicare_dezechilibru(X: pd.DataFrame, y: pd.Series, strategie: str) -> pd.DataFrame:
	if strategie == "Undersampling":
		sampler = RandomUnderSampler()
	elif strategie == "Oversampling":
		sampler = RandomOverSampler()
	elif strategie == "ADASYN":
		sampler = ADASYN()
	else:
		return X, y
	return sampler.fit_resample(X, y)


def aplicare_scalare(X: pd.DataFrame, metoda: str):
	scaler = None
	if metoda == "StandardScaler":
		scaler = StandardScaler()
	elif metoda == "MinMaxScaler":
		scaler = MinMaxScaler()
	elif metoda == "RobustScaler":
		scaler = RobustScaler()

	if scaler:
		cols_to_scale = X.select_dtypes(include=["number"]).columns
		X[cols_to_scale] = scaler.fit_transform(X[cols_to_scale])
	return X


def impartire_train_test(X: pd.DataFrame, y: pd.Series, setari: dict):
	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=setari["proportie_test"],
		stratify=y if setari["stratificat"] else None,
		random_state=42,
	)

	tinta = setari["tinta"]

	X_train = pd.DataFrame(X_train, columns=X.columns).reset_index(drop=True)
	X_test = pd.DataFrame(X_test, columns=X.columns).reset_index(drop=True)
	y_train = pd.Series(y_train, name=tinta).reset_index(drop=True)
	y_test = pd.Series(y_test, name=tinta).reset_index(drop=True)

	for df, nume in zip([X_train, X_test, y_train, y_test], ["X_train", "X_test", "y_train", "y_test"]):
		salvare_date_temp(df, nume)


def procesare_dataset(df: pd.DataFrame, dict_procesare: dict):
	# Eliminare coloane
	if dict_procesare.get("coloane_eliminate"):
		df = eliminare_coloane(df, dict_procesare["coloane_eliminate"])

	# Eliminare duplicate
	if dict_procesare.get("eliminare_duplicate"):
		df = eliminare_duplicate(df)

	# Eliminare rânduri cu multe valori lipsă
	if dict_procesare.get("eliminare_randuri_nan"):
		df = eliminare_randuri_nan(df)

	# Tratare outlieri
	if "outlieri" in dict_procesare:
		metoda = dict_procesare["outlieri"]["detectie"]
		actiune = dict_procesare["outlieri"]["actiune"]
		df = tratare_outlieri(df, metoda, actiune)

	# Completare valori lipsă
	if "valori_lipsa" in dict_procesare:
		df = completare_valori_lipsa(df, dict_procesare["valori_lipsa"])

	# Conversie coloane binare
	if "coloane_binare" in dict_procesare:
		df = conversie_coloane_binare(df, dict_procesare["coloane_binare"])

	# Procesare datetime
	if "datetime" in dict_procesare:
		df = aplicare_datetime(df, dict_procesare["datetime"])

	# Salvăm tinta pentru split ulterior
	tinta = dict_procesare["impartire"]["tinta"]
	X = df.drop(columns=[tinta])
	y = df[tinta]

	# Encoding
	if "encoding" in dict_procesare:
		X = aplicare_encoding(X, dict_procesare["encoding"])

	# Dezechilibru
	if dict_procesare.get("dezechilibru") != "Niciuna":
		X, y = aplicare_dezechilibru(X, y, dict_procesare["dezechilibru"])

	# Scalare
	if dict_procesare.get("scalare") != "Niciuna":
		X = aplicare_scalare(X, dict_procesare["scalare"])

	# Împărțire train/test
	setari_split = dict_procesare["impartire"]
	setari_split["tinta"] = tinta
	impartire_train_test(X, y, setari_split)
