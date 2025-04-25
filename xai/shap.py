import matplotlib.pyplot as plt
import shap


def get_shap_explainer(model_wrapper, X_train, sample_size):
	model = model_wrapper.model

	if model_wrapper.tip == "liniar":
		return shap.LinearExplainer(model, X_train)

	elif model_wrapper.tip == "non-liniar":
		return shap.KernelExplainer(
			model.predict,
			X_train.sample(
				n=sample_size if X_train.shape[0] > sample_size else X_train.shape[0],
				random_state=42,
			),
		)

	elif model_wrapper.tip == "arbore":
		return shap.TreeExplainer(model)

	elif model_wrapper.tip == "deep":
		return shap.DeepExplainer(model, X_train)

	else:
		raise ValueError("Tipul specificat nu este recunoscut.")


def get_shap_values(shap_explainer, X_test, sample_size):
	return shap_explainer(
		X_test.sample(n=sample_size if X_test.shape[0] > sample_size else X_test.shape[0], random_state=42)
	)

	# X_test_array = np.array(X_test) if isinstance(self.model_wrapper, model_wrappers.Sequential) else X_test
	# return shap_explainer(X_test_array[:sample_size])


def calculate_shap_values(model_wrapper, X_train, X_test, sample_size=25):
	shap_explainer = get_shap_explainer(model_wrapper, X_train, sample_size)
	shap_values = get_shap_values(shap_explainer, X_test, sample_size)
	return shap_values


def bar_plot(shap_values):
	fig = plt.figure()
	shap.plots.bar(shap_values, max_display=5, show=False)
	return fig


def waterfall_plot(shap_values, instanta=0):
	fig = plt.figure()
	shap.plots.waterfall(shap_values[instanta], max_display=5, show=False)
	return fig


def violin_plot(shap_values):
	fig = plt.figure()
	shap.plots.violin(shap_values, max_display=5, show=False)
	return fig
