from keras import models
import lime
import lime.lime_tabular
import numpy as np
import pandas as pd
import streamlit as st


def get_explanation(model, X_train: pd.DataFrame, X_test: pd.DataFrame, instanta=0):
	explainer = lime.lime_tabular.LimeTabularExplainer(
		training_data=X_train.values,
		feature_names=X_train.columns,
		class_names=["Frauda", "Legitima"],  # ?
		mode="classification",
	)

	instance = X_test.values[instanta]

	if hasattr(model.model, "predict_proba"):
		predict_fn = model.model.predict_proba
	elif isinstance(model.model, models.Sequential):

		def predict_fn(X):
			probs = model.model.predict(X)
			return np.hstack([1 - probs, probs])

	explanation = explainer.explain_instance(data_row=instance, predict_fn=predict_fn)
	return explanation


def explanation_plot(explanation, key):
	lime_html = (
		f"<div style='background-color: white; padding: 10px;'>{explanation.as_html()}</div>"
	)
	st.session_state.lime[key] = lime_html

	# explanation_list = explanation.as_list()
	# features, importances = zip(*explanation_list)
	# explanation_df = pd.DataFrame({"Feature": features, "Importance": importances})
	# fig, ax = plt.subplots(figsize=(10, 6))
	# sns.barplot(
	# 	x="Importance",
	# 	y="Feature",
	# 	hue="Feature",
	# 	legend=False,
	# 	data=explanation_df,
	# 	palette="rocket",
	# 	ax=ax,
	# )
	# ax.set_xlabel("Feature Importance")
	# ax.set_title(f"LIME Feature Importance for Instance Index {instanta}")
	# ax.grid(axis="x", linestyle="--", alpha=0.7)

	# st.pyplot(fig)
