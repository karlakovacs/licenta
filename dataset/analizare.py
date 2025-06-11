import json
import os
import tempfile

import pandas as pd


def generare_metadate(df: pd.DataFrame, max_valori_unice: int = 15):
	variabile = {}

	for col in df.columns:
		serie = df[col].dropna()
		tip = serie.dtype

		# 1. Boolean
		if pd.api.types.is_bool_dtype(tip):
			valori = sorted(map(str, set(serie.unique())))
			variabile[col] = {"tip": "B", "valori": valori}
			continue

		if serie.nunique() == 2 and set(serie.unique()).issubset({0, 1, True, False}):
			variabile[col] = {"tip": "B", "valori": sorted(map(str, set(serie)))}
			continue

		# 2. Numeric
		if pd.api.types.is_numeric_dtype(tip):
			if (serie % 1 == 0).all():
				tip_numeric = "ND"
				val_min = int(serie.min())
				val_max = int(serie.max())

			else:
				tip_numeric = "NC"
				val_min = float(serie.min())
				val_max = float(serie.max())

			variabile[col] = {"tip": tip_numeric, "min": val_min, "max": val_max}
			continue

		# 3. Categorial sau text
		unice = serie.nunique()
		if unice <= max_valori_unice:
			categorii = serie.value_counts().sort_values(ascending=False).index.tolist()
			variabile[col] = {"tip": "C", "valori": list(map(str, categorii))}
		else:
			variabile[col] = {"tip": "T"}

	denumire_fisier = "metadate.json"
	temp_path = os.path.join(tempfile.gettempdir(), denumire_fisier)
	with open(temp_path, "w", encoding="utf-8") as f:
		json.dump(variabile, f, indent=2, ensure_ascii=False)


def generare_metadate_set_procesat(df: pd.DataFrame, max_valori_unice: int = 15) -> dict:
	variabile_categoriale = []
	variabile_numerice = []
	variabile_booleene = []

	for col in df.columns:
		col_data = df[col]
		n_unique = col_data.dropna().nunique()

		is_bool = pd.api.types.is_bool_dtype(col_data)
		is_object = pd.api.types.is_object_dtype(col_data)

		if is_bool or is_object or n_unique <= max_valori_unice:
			variabile_categoriale.append(col)
		else:
			variabile_numerice.append(col)

		if is_bool or n_unique == 2:
			variabile_booleene.append(col)

	variabile: dict = {
		"variabile_categoriale": variabile_categoriale,
		"variabile_numerice": variabile_numerice,
		"variabile_booleene": variabile_booleene,
	}

	return variabile
