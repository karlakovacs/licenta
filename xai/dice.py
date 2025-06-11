import dice_ml
from dice_ml import Dice, Model
import pandas as pd


def pregatire_date(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()
	for col in df.columns:
		col_vals = df[col].dropna().unique()

		if set(col_vals).issubset({"True", "False"}):
			df[col] = df[col].map({"False": 0, "True": 1})

		elif all(isinstance(v, bytes) and v in [b"True", b"False"] for v in col_vals):
			df[col] = df[col].apply(lambda x: 1 if x == b"True" else 0)

		elif df[col].dtype == bool:
			df[col] = df[col].astype(int)

		elif df[col].dtype == object:
			try:
				df[col] = pd.to_numeric(df[col])
			except:
				pass

	return df


def get_dice_data(X_train: pd.DataFrame, y_train: pd.Series, metadate: dict) -> dice_ml.Data:
	X_train = pregatire_date(X_train)
	variabile_categoriale = metadate["variabile_categoriale"]
	variabile_numerice = metadate["variabile_numerice"]

	df = pd.concat([X_train.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1)

	return dice_ml.Data(
		dataframe=df,
		outcome_name=y_train.name,
		continuous_features=variabile_numerice,
		categorical_features=variabile_categoriale,
	)


def get_dice_model(model, model_type: str = "classifier") -> Model:
	if hasattr(model, "layers"):  # keras
		return Model(model=model, backend="TF2", model_type=model_type)

	elif hasattr(model, "predict_proba"):  # sklearn-like
		return Model(model=model, backend="sklearn", model_type=model_type)

	else:
		raise ValueError("Modelul nu este compatibil cu DiCE.")


def get_dice_explainer(model, X_train: pd.DataFrame, y_train: pd.Series, metadate: dict) -> Dice:
	data = get_dice_data(X_train, y_train, metadate)
	dice_model = get_dice_model(model)
	return Dice(data, dice_model, method="random")


def descriere_diferente(
	X_explicat: pd.DataFrame, counterfactuals: pd.DataFrame, metadate: dict
) -> dict[int, list[dict]]:
	variabile_numerice = metadate["variabile_numerice"]
	variabile_booleene = metadate["variabile_booleene"]
	explicatii_total = {}
	orig = X_explicat.iloc[0]

	for i in range(len(counterfactuals)):
		cf = counterfactuals.iloc[i]
		explicatii = []

		for col in cf.index:
			val_init = orig[col]
			val_cf = cf[col]

			if val_init != val_cf:
				# if isinstance(val_init, (int, float)) and isinstance(val_cf, (int, float)):
				if col in variabile_numerice:
					delta = val_cf - val_init
					explicatii.append(
						{
							"variabila": col,
							"tip": "N",
							"directie": "+" if delta > 0 else "-",
							"valoare": round(abs(delta), 4),
						}
					)
				elif col in variabile_booleene:
					explicatii.append({"variabila": col, "tip": "B", "valoare": bool(val_cf)})

				else:
					explicatii.append({"variabila": col, "tip": "C", "valoare": val_cf})

		explicatii_total[i] = explicatii

	return explicatii_total


def filter_counterfactuals(counterfactuals: pd.DataFrame, X_explicat: pd.DataFrame) -> pd.DataFrame:
	orig = X_explicat.iloc[0]
	dif_cols = [col for col in counterfactuals.columns if not (counterfactuals[col] == orig[col]).all()]
	return counterfactuals[dif_cols]


def calculate_counterfactuals(
	explainer: Dice, X_explicat: pd.DataFrame, coloane: list, metadate: dict
) -> tuple[pd.DataFrame, dict, str]:
	try:
		X_explicat = pregatire_date(X_explicat)
		dice_exp = explainer.generate_counterfactuals(X_explicat, total_CFs=3, desired_class="opposite")
		counterfactuals = dice_exp.cf_examples_list[0].final_cfs_df[coloane]
		counterfactuals = filter_counterfactuals(counterfactuals, X_explicat)
		explicatii = descriere_diferente(X_explicat, counterfactuals, metadate)
		interpretari = interpretare_explicatii(explicatii)
		return counterfactuals, explicatii, interpretari
	except:
		return None, None, None


def interpretare_explicatii(explicatii: dict) -> str:
	if explicatii is None:
		return None
	
	output = ""

	for idx, modificari in explicatii.items():
		output += f"#### Contrafactual {idx + 1}\n"

		for m in modificari:
			if m["tip"] == "N":
				directie = "crească" if m["directie"] == "+" else "scadă"
				output += f"- `{m['variabila']}` trebuie să **{directie} cu {m['valoare']}**\n"
			elif m["tip"] == "B":
				output += f"- `{m['variabila']}` trebuie să fie **`{m['valoare']}`**\n"
			elif m["tip"] == "C":
				output += f"- `{m['variabila']}` trebuie să aibă valoarea **`{m['valoare']}`**\n"

		output += "\n"

	return output
