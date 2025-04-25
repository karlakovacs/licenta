import warnings

import dice_ml
from dice_ml import Dice, Model
from dice_ml.utils import helpers
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin


class SklearnLikeWrapper(BaseEstimator, ClassifierMixin):
	def __init__(self, model):
		self.model = model

	def predict(self, X):
		return self.model.predict(X)

	def predict_proba(self, X):
		return self.model.predict_proba(X)


def get_dice_data(X_train: pd.DataFrame, y_train: pd.Series, target_col: str) -> dice_ml.Data:
	return dice_ml.Data(
		dataframe=pd.concat([X_train.reset_index(drop=True), y_train.reset_index(drop=True)], axis=1),
		continuous_features=X_train.columns.tolist(),
		outcome_name=target_col,
	)


def get_dice_model(model, model_type: str = "classifier") -> Model:
	try:
		if isinstance(model, BaseEstimator):
			return Model(model=model, backend="sklearn", model_type=model_type)

		if hasattr(model, "predict") and hasattr(model, "predict_proba"):
			wrapped = SklearnLikeWrapper(model)
			return Model(model=wrapped, backend="sklearn", model_type=model_type)

		import keras

		if isinstance(model, keras.Model):
			return Model(model=model, backend="TF2", model_type=model_type)

	except Exception as e:
		warnings.warn(f"Eroare la crearea modelului DiCE: {e}")
		raise

	raise ValueError("Modelul nu este compatibil cu DiCE")


def get_dice_explainer(model, X_train: pd.DataFrame, y_train: pd.Series, target_col: str) -> Dice:
	data = get_dice_data(X_train, y_train, target_col)
	dice_model = get_dice_model(model)
	return Dice(data, dice_model, method="random")
