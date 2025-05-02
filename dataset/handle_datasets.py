import os

import streamlit as st


os.environ["KAGGLE_USERNAME"] = st.secrets.kaggle.KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = st.secrets.kaggle.KAGGLE_KEY


import tempfile

from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd


def citire_fisier_local():
	fisier = st.file_uploader("Încarcă un fișier", type=["csv", "xlsx"])
	if fisier is not None:
		if fisier.name.endswith(".csv"):
			df = pd.read_csv(fisier)
		elif fisier.name.endswith(".xlsx"):
			df = pd.read_excel(fisier)
		else:
			st.error("Format de fișier necunoscut!")
		
		return df


def descarcare_kaggle(link: str) -> pd.DataFrame:
	prefix = "https://www.kaggle.com/datasets/"
	if not link.startswith(prefix):
		raise ValueError("Linkul trebuie să înceapă cu 'https://www.kaggle.com/datasets/'")
	dataset_path = link.replace(prefix, "").strip("/")
	api = KaggleApi()
	api.authenticate()

	temp_dir = tempfile.mkdtemp(prefix="kaggle_")
	api.dataset_download_files(dataset_path, path=temp_dir, unzip=True)

	for file in os.listdir(temp_dir):
		if file.endswith(".csv") or file.endswith(".xlsx"):
			file_path = os.path.join(temp_dir, file)
			if file.endswith(".csv"):
				return pd.read_csv(file_path)
			else:
				return pd.read_excel(file_path)

	raise FileNotFoundError("Nu s-a găsit niciun fișier .csv sau .xlsx în arhiva descărcată.")
