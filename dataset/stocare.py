import json
import os
import pickle
import tempfile

import pandas as pd


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


def citire_metadate() -> dict:
	denumire_fisier = "metadate.json"
	temp_path = os.path.join(tempfile.gettempdir(), denumire_fisier)
	with open(temp_path, "r") as f:
		return json.load(f)
