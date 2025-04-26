import matplotlib.pyplot as plt
import numpy as np
import shap


def get_shap_explainer(model, X_train, sample_size=50):
	if hasattr(model, "layers"):  # deep learning
		return shap.DeepExplainer(model, X_train)

	elif hasattr(model, "tree_") or hasattr(model, "estimators_"):  # arbori
		return shap.TreeExplainer(model)

	elif hasattr(model, "coef_"):  # liniar
		return shap.LinearExplainer(model, X_train)

	else:  # default: non-liniar
		X_train_sample = X_train.iloc[:sample_size]
		return shap.KernelExplainer(model.predict, X_train_sample)


def calculate_shap_values(model, X_train, X_test):
	explainer = get_shap_explainer(model, X_train)
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


def bar_plot(shap_values):
	fig = plt.figure()
	shap.plots.bar(shap_values, max_display=5, show=False)
	return fig


def waterfall_plot(shap_values, instanta):
	fig = plt.figure()
	shap.plots.waterfall(shap_values[instanta], max_display=5, show=False)
	return fig


def violin_plot(shap_values):
	fig = plt.figure()
	shap.plots.violin(shap_values, max_display=5, show=False)
	return fig
