import matplotlib.pyplot as plt
import shap


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
