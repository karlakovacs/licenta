import matplotlib.pyplot as plt
import numpy as np
import shap
import streamlit as st


def bar_plot(shap_values, key):
	fig = plt.figure()
	shap.plots.bar(shap_values, max_display=5, show=False)
	st.session_state.bar[key] = fig


def waterfall_plot(shap_values, key, instanta=0):
	fig = plt.figure()
	shap.plots.waterfall(shap_values[instanta], max_display=5, show=False)
	st.session_state.waterfall[key] = fig

def violin_plot(shap_values, key):
	fig = plt.figure()
	shap.plots.violin(shap_values, max_display=5, show=False)
	st.session_state.violin[key] = fig
