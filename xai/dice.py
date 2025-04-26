import dice_ml
from dice_ml import Dice, Model
import dice_ml.explainer_interfaces
import dice_ml.explainer_interfaces.explainer_base
import pandas as pd


# class SklearnLikeWrapper(BaseEstimator, ClassifierMixin):
# 	def __init__(self, model):
# 		self.model = model

# 	def predict(self, X):
# 		return self.model.predict(X)

# 	def predict_proba(self, X):
# 		return self.model.predict_proba(X)

# def get_dice_model(model, model_type: str = "classifier") -> Model:
# 	try:
# 		if isinstance(model, BaseEstimator):
# 			return Model(model=model, backend="sklearn", model_type=model_type)

# 		if hasattr(model, "predict") and hasattr(model, "predict_proba"):
# 			wrapped = SklearnLikeWrapper(model)
# 			return Model(model=wrapped, backend="sklearn", model_type=model_type)

# 		import keras

# 		if isinstance(model, keras.Model):
# 			return Model(model=model, backend="TF2", model_type=model_type)

# 	except Exception as e:
# 		warnings.warn(f"Eroare la crearea modelului DiCE: {e}")
# 		raise

# 	raise ValueError("Modelul nu este compatibil cu DiCE")


def get_dice_data(X_train: pd.DataFrame, y_train: pd.Series, tinta: str) -> dice_ml.Data:
	return dice_ml.Data(
		dataframe=pd.concat([X_train.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1),
		continuous_features=X_train.columns.tolist(),
		outcome_name=tinta,
	)


def get_dice_model(model, model_type: str = "classifier") -> Model:
	if hasattr(model, "layers"):  # keras
		return Model(model=model, backend="TF2", model_type=model_type)

	elif hasattr(model, "predict_proba"):  # sklearn-like
		return Model(model=model, backend="sklearn", model_type=model_type)

	else:
		raise ValueError("Modelul nu este compatibil cu DiCE.")


def get_dice_explainer(model, X_train: pd.DataFrame, y_train: pd.Series, tinta: str) -> Dice:
	data = get_dice_data(X_train, y_train, tinta)
	dice_model = get_dice_model(model)
	return Dice(data, dice_model, method="random")


def calculate_counterfactuals(model, explainer: Dice, date_instanta, X_train_columns):
	predictie = model.predict(date_instanta)

	if hasattr(model, "layers"):  # keras
		predictie = int(predictie > 0.5)
	else:
		predictie = predictie[0]

	dice_exp = explainer.generate_counterfactuals(date_instanta, total_CFs=3, desired_class="opposite")

	cf_df = dice_exp.cf_examples_list[0].final_cfs_df[X_train_columns]
	diffs = cf_df - date_instanta.values

	return predictie, cf_df, diffs
