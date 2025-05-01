import lime
from lime.explanation import Explanation
from lime.lime_tabular import LimeTabularExplainer
import matplotlib.figure as plt
import numpy as np
import pandas as pd


def get_explanation(model, X_train: pd.DataFrame, X_test: pd.DataFrame, instanta=0) -> Explanation:
	try:
		explainer = LimeTabularExplainer(
			training_data=X_train.values,
			feature_names=X_train.columns,
			class_names=[str(c) for c in model.classes_],
			mode="classification",
		)

		instance = X_test.values[instanta]

		if hasattr(model, "predict_proba"):
			predict_fn = model.predict_proba
		else:  # keras

			def predict_fn(X):
				probs = model.predict(X)
				return np.hstack([1 - probs, probs])

		explanation = explainer.explain_instance(data_row=instance, predict_fn=predict_fn)
		return explanation
	except:
		return None


def explanation_plot(explanation: Explanation) -> str:
	lime_html = f"<div style='background-color: white; padding: 10px;'>{explanation.as_html()}</div>"
	return lime_html

def explanation_pyplot(explanation: Explanation) -> plt.Figure:
	return explanation.as_pyplot_figure(label=1)





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
