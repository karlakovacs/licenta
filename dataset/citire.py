import os
import pickle
import tempfile

import pandas as pd
import streamlit as st


os.environ["KAGGLE_USERNAME"] = st.secrets.kaggle.KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = st.secrets.kaggle.KAGGLE_KEY


from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd


def optimizare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
	if df is None:
		return None

	optimized_df = df.copy()

	for col in optimized_df.columns:
		col_data = optimized_df[col]

		# 1. datetime
		if col_data.dtypes == object:
			try:
				optimized_df[col] = pd.to_datetime(col_data, errors="raise")
				continue
			except (ValueError, TypeError):
				pass

		# 2. boolean
		if pd.api.types.is_numeric_dtype(col_data):
			unique_vals = col_data.dropna().unique()
			if set(unique_vals).issubset({0, 1}):
				optimized_df[col] = col_data.astype(bool)
				continue

		# 3. category
		if col_data.dtypes == object:
			num_unique = col_data.nunique()
			# num_total = len(col_data)
			# if num_unique / num_total < 0.5:
			if num_unique <= 15:
				optimized_df[col] = col_data.astype("category")
				continue

		# 4. integer & float
		if pd.api.types.is_integer_dtype(col_data):
			optimized_df[col] = pd.to_numeric(col_data, downcast="integer")
		elif pd.api.types.is_float_dtype(col_data):
			optimized_df[col] = pd.to_numeric(col_data, downcast="float")

	return optimized_df


def citire_fisier_local():
	fisier = st.file_uploader("📄 Încarcă un fișier", type=["csv", "xlsx"])
	if fisier is not None:
		if fisier.name.endswith(".csv"):
			df = pd.read_csv(fisier)
		elif fisier.name.endswith(".xlsx"):
			df = pd.read_excel(fisier)
		else:
			st.error("Format de fișier necunoscut!")
		return optimizare_dataframe(df)


def citire_kaggle(link: str) -> pd.DataFrame:
	prefix = "https://www.kaggle.com/datasets/"
	if not link.startswith(prefix):
		raise ValueError("Link-ul trebuie să înceapă cu 'https://www.kaggle.com/datasets/'")
	dataset_path = link.replace(prefix, "").strip("/")
	api = KaggleApi()
	api.authenticate()

	temp_dir = tempfile.mkdtemp(prefix="kaggle_")
	api.dataset_download_files(dataset_path, path=temp_dir, unzip=True)

	for file in os.listdir(temp_dir):
		if file.endswith(".csv") or file.endswith(".xlsx"):
			file_path = os.path.join(temp_dir, file)
			df = None
			if file.endswith(".csv"):
				df = pd.read_csv(file_path)
			else:
				df = pd.read_excel(file_path)
			return optimizare_dataframe(df)

	raise FileNotFoundError("Nu s-a găsit niciun fișier .csv sau .xlsx în arhiva descărcată.")


def citire_set_date(set_date: dict) -> pd.DataFrame:
	if set_date["sursa"] != "Seturi predefinite":
		return citire_date_temp(set_date["denumire"])
	return citire_date_predefinite(set_date["denumire"])


def citire_date_predefinite(nume_dataset: str) -> pd.DataFrame:
	df = pd.read_parquet(f"data/{nume_dataset.lower()}.parquet")
	return df


def citire_date_temp(nume_dataset: str) -> pd.DataFrame | pd.Series:
	temp_path = tempfile.gettempdir() + "/" + nume_dataset + ".pkl"
	with open(temp_path, "rb") as f:
		return pickle.load(f)


def salvare_date_temp(df: pd.DataFrame | pd.Series, nume_dataset: str) -> None:
	temp_path = tempfile.gettempdir() + "/" + nume_dataset + ".pkl"
	with open(temp_path, "wb") as f:
		pickle.dump(df, f)
