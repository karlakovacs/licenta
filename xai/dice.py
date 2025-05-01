import dice_ml
from dice_ml import Dice, Model
from lightgbm import LGBMClassifier
import pandas as pd
from xgboost import XGBClassifier


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


def get_features(df: pd.DataFrame):
	categorical_features = [col for col in df.columns if df[col].dtype.name in ["bool", "category", "object"]]
	continuous_features = [col for col in df.columns if col not in categorical_features]
	return categorical_features, continuous_features


def get_dice_data(X_train: pd.DataFrame, y_train: pd.Series, tinta: str, model) -> dice_ml.Data:
	if isinstance(model, (XGBClassifier, LGBMClassifier)):
		X_train = pregatire_date(X_train)
		categorical_features, continuous_features = get_features(X_train)
	else:
		categorical_features, continuous_features = get_features(X_train)
		X_train = pregatire_date(X_train)

	df = pd.concat([X_train.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1)

	return dice_ml.Data(
		dataframe=df,
		outcome_name=tinta,
		continuous_features=continuous_features,
		categorical_features=categorical_features,
	)


def get_dice_model(model, model_type: str = "classifier") -> Model:
	if hasattr(model, "layers"):  # keras
		return Model(model=model, backend="TF2", model_type=model_type)

	elif hasattr(model, "predict_proba"):  # sklearn-like
		return Model(model=model, backend="sklearn", model_type=model_type)

	else:
		raise ValueError("Modelul nu este compatibil cu DiCE.")


def get_dice_explainer(model, X_train: pd.DataFrame, y_train: pd.Series, tinta: str) -> Dice:
	data = get_dice_data(X_train, y_train, tinta, model)
	dice_model = get_dice_model(model)
	return Dice(data, dice_model, method="random")


def descriere_diferente(date_instanta: pd.DataFrame, contrafactuale: pd.DataFrame) -> dict[int, list[dict]]:
	explicatii_total = {}
	orig = date_instanta.iloc[0]

	for i in range(len(contrafactuale)):
		cf = contrafactuale.iloc[i]
		explicatii = []

		for col in cf.index:
			val_init = orig[col]
			val_cf = cf[col]

			if val_init != val_cf:
				if isinstance(val_init, (int, float)) and isinstance(val_cf, (int, float)):
					delta = val_cf - val_init
					explicatii.append(
						{
							"variabila": col,
							"tip": "numeric",
							"directie": "+" if delta > 0 else "-",
							"valoare": round(abs(delta), 4),
						}
					)
				else:
					explicatii.append({"variabila": col, "tip": "categoric", "valoare": val_cf})

		explicatii_total[i] = explicatii

	return explicatii_total


def filtrare_contrafactuale(cf_df: pd.DataFrame, date_instanta: pd.DataFrame) -> pd.DataFrame:
	orig = date_instanta.iloc[0]
	dif_cols = [col for col in cf_df.columns if not (cf_df[col] == orig[col]).all()]
	return cf_df[dif_cols]


def calculate_counterfactuals(
	model, explainer: Dice, date_instanta, X_train_columns
) -> tuple[int | bool, pd.DataFrame, dict]:
	try:
		predictie = model.predict(date_instanta)
		print("predictie ok")

		if hasattr(model, "layers"):  # keras
			predictie = int(predictie > 0.5)
		else:
			predictie = predictie[0]

		date_instanta = pregatire_date(date_instanta)
		dice_exp = explainer.generate_counterfactuals(date_instanta, total_CFs=3, desired_class="opposite")
		cf_df = dice_exp.cf_examples_list[0].final_cfs_df[X_train_columns]
		cf_df = filtrare_contrafactuale(cf_df, date_instanta)
		explicatii = descriere_diferente(date_instanta, cf_df)
		return predictie, cf_df, explicatii
	except:
		return None, None, None


def interpretare_explicatii(explicatii: dict) -> str:
	output = ""

	for idx, modificari in explicatii.items():
		output += f"#### Contrafactual #{idx + 1}\n"

		for m in modificari:
			if m["tip"] == "numeric":
				directie = "crească" if m["directie"] == "+" else "scadă"
				output += f"- `{m['variabila']}` trebuie să **{directie} cu {m['valoare']}**\n"
			else:
				output += f"- `{m['variabila']}` trebuie să aibă valoarea **`{m['valoare']}`**\n"

		output += "\n"

	return output
