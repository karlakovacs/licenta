import os

import pandas as pd
import streamlit as st


os.environ["KAGGLE_USERNAME"] = st.secrets.kaggle.KAGGLE_USERNAME
os.environ["KAGGLE_KEY"] = st.secrets.kaggle.KAGGLE_KEY


from kaggle.api.kaggle_api_extended import KaggleApi


def descarcare_kaggle(link: str) -> tuple[pd.DataFrame, str]:
	prefix = "https://www.kaggle.com/datasets/"
	if not link.startswith(prefix):
		raise ValueError("Linkul trebuie să înceapă cu 'https://www.kaggle.com/datasets/'")

	# Extragere nume complet (ex: "username/dataset")
	dataset_path = link.replace(prefix, "").strip("/")

	# Doar numele datasetului
	nume_dataset = dataset_path.split("/")[-1]

	# Autentificare API
	api = KaggleApi()
	api.authenticate()

	os.makedirs("data_kaggle", exist_ok=True)
	api.dataset_download_files(dataset_path, path="data_kaggle", unzip=True)

	for file in os.listdir("data_kaggle"):
		if file.endswith(".csv") or file.endswith(".xlsx"):
			file_path = os.path.join("data_kaggle", file)
			if file.endswith(".csv"):
				return pd.read_csv(file_path), nume_dataset
			else:
				return pd.read_excel(file_path), nume_dataset

	raise FileNotFoundError("Nu s-a găsit niciun fișier .csv sau .xlsx în arhiva descărcată.")
