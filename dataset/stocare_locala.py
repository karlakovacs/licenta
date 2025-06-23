import json
import os
import pickle
import tempfile

import pandas as pd

from .gestionare import citire_date_predefinite


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


def citire_set_date(set_date: dict) -> pd.DataFrame:
	if set_date["sursa"] != "Seturi predefinite":
		return citire_date_temp(set_date["denumire"])
	return citire_date_predefinite(set_date["denumire"])
