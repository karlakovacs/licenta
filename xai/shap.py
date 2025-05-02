import matplotlib.pyplot as plt
import numpy as np
import shap


class PredictWrapper:
	def __init__(self, model):
		self.model = model

	def __call__(self, X):
		return self.model.predict(X)


def get_shap_explainer(model, X_train, sample_size=100):
	from shap.explainers import Deep, Kernel, Linear, Tree

	try:
		return Deep(model, X_train)
	except Exception as e:
		pass

	try:
		return Tree(model)
	except Exception as e:
		pass

	try:
		return Linear(model, X_train)
	except Exception as e:
		pass

	try:
		X_train_sample = X_train.iloc[:sample_size]
		return Kernel(PredictWrapper(model), X_train_sample)
	except Exception as e:
		return None


def calculate_shap_values(model, X_train, X_test):
	explainer = get_shap_explainer(model, X_train)
	if explainer is not None:
		explanation = explainer(X_test.values)

		if isinstance(explainer, shap.explainers._deep.DeepExplainer):
			if explanation.values.ndim == 3:
				values = explanation.values.squeeze()
			else:
				values = explanation.values

			n_samples = values.shape[0]

			base_val = explanation.base_values
			if base_val is None:
				base_val = getattr(explainer, "expected_value", None)

			if base_val is not None:
				if np.isscalar(base_val):
					base_val = np.repeat(base_val, n_samples)
				else:
					base_val = np.array(base_val)

				if base_val.shape[0] != n_samples:
					base_val = np.repeat(base_val[0], n_samples)
			else:
				base_val = np.zeros(n_samples)

			return shap.Explanation(
				values=values, base_values=base_val, data=X_test.values[:n_samples], feature_names=X_test.columns.tolist()
			)
		else:
			return explanation
	else:
		return "Error"


def bar_plot(shap_values):
	try:
		fig = plt.figure(figsize=(10, 3))
		shap.plots.bar(shap_values, max_display=5, show=False)
		return fig
	except Exception as e:
		return None


def waterfall_plot(shap_values, instanta):
	try:
		fig = plt.figure(figsize=(10, 3))
		shap.plots.waterfall(shap_values[instanta], max_display=5, show=False)
		return fig
	except Exception as e:
		return None

def violin_plot(shap_values):
	try:
		fig = plt.figure(figsize=(10, 3))
		shap.plots.violin(shap_values, max_display=5, show=False)
		return fig
	except Exception as e:
		return None
