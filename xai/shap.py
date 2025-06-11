import matplotlib.pyplot as plt
import pandas as pd
import shap


class CallableModel:
	def __init__(self, model):
		self.model = model

	def __call__(self, X):
		return self.model.predict_proba(X)


def pregatire_date(df: pd.DataFrame) -> pd.DataFrame:
	df = df.copy()

	for col in df.columns:
		if df[col].dtype == "bool":
			df[col] = df[col].astype(int)

		elif df[col].dtype == "object":
			try:
				df[col] = pd.to_numeric(df[col])
			except ValueError:
				df[col] = df[col].astype("category").cat.codes  # Encode categoric

	return df


def get_shap_explainer(model, X_train: pd.DataFrame, denumire_model: str):
	X_train = pregatire_date(X_train)

	if denumire_model in [
		"Random Forest",
		"Balanced Random Forest",
		"Decision Tree",
		"Gradient Boosting Classifier",
		"XGBoost",
		"LightGBM",
		"CatBoost",
	]:
		explainer = shap.TreeExplainer(model, X_train)

	elif denumire_model in ["Logistic Regression", "Linear Discriminant Analysis"]:
		explainer = shap.LinearExplainer(model, X_train)

	elif denumire_model in [
		"Quadratic Discriminant Analysis",
		"K-Nearest Neighbors",
		"Support Vector Classifier",
		"AdaBoost",
	]:
		explainer = shap.Explainer(CallableModel(model), X_train)

	elif denumire_model == "Multilayer Perceptron":
		explainer = shap.Explainer(model, X_train)

	else:
		explainer = None

	return explainer


def calculate_shap_values(explainer, X_test: pd.DataFrame) -> shap.Explanation:
	X_test = pregatire_date(X_test)
	
	if explainer is None:
		return None
	if  isinstance(explainer, shap.TreeExplainer):
		shap_values = explainer(X_test, check_additivity=False)
	else:
		shap_values = explainer(X_test)
	if len(shap_values.shape) == 3:
		shap_values = shap_values[:, :, 1]
	return shap_values


def shap_plot(shap_values):
	fig = plt.figure(figsize=(10, 3))
	shap.plots.waterfall(shap_values[0])
	return fig
