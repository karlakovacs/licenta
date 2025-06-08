import json
import os
import tempfile

import pandas as pd


def generare_metadate_json(df: pd.DataFrame, prag_text=15):
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
		if unice <= prag_text:
			categorii = serie.value_counts().sort_values(ascending=False).index.tolist()
			variabile[col] = {"tip": "C", "valori": list(map(str, categorii))}
		else:
			variabile[col] = {"tip": "T"}

	temp_path = os.path.join(tempfile.gettempdir(), "metadate.json")
	with open(temp_path, "w", encoding="utf-8") as f:
		json.dump(variabile, f, indent=2, ensure_ascii=False)

	# print(variabile)

	return temp_path
