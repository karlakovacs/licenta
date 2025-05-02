import lime
from lime.explanation import Explanation
from lime.lime_tabular import LimeTabularExplainer
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def get_explanation(
	model, X_train: pd.DataFrame, X_test: pd.DataFrame, instanta: int, max_valori_unice: int = 10
) -> Explanation:
	try:
		categorical_features = [
			idx
			for idx, col in enumerate(X_train.columns)
			if (
				X_train[col].dtype == "bool"
				or X_train[col].dtype.name == "category"
				or X_train[col].dtype == "object"
				or (np.issubdtype(X_train[col].dtype, np.integer) and X_train[col].nunique() <= max_valori_unice)
			)
		]

		explainer = LimeTabularExplainer(
			training_data=X_train.to_numpy(),
			feature_names=X_train.columns,
			class_names=[str(c) for c in model.classes_],
			categorical_features=categorical_features,
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


# def explanation_plot(explanation: Explanation) -> str:
# 	lime_html = f"<div style='background-color: white; padding: 10px;'>{explanation.as_html()}</div>"
# 	return lime_html


def explanation_plotly(explanation: Explanation) -> go.Figure:
	lime_results = sorted(explanation.as_list(), key=lambda x: abs(x[1]), reverse=True)

	features = [desc for desc, _ in lime_results]
	weights = [weight for _, weight in lime_results]
	colors = ["green" if w > 0 else "red" for w in weights]
	labels = ["Contribuții pozitive" if w > 0 else "Contribuții negative" for w in weights]

	class_names = explanation.class_names if hasattr(explanation, "class_names") else ["Class 0", "Class 1"]
	predicted_class_idx = explanation.predict_proba.argmax()
	predicted_class = class_names[predicted_class_idx]
	prediction_prob = explanation.predict_proba[predicted_class_idx]

	fig = go.Figure()

	fig.add_trace(
		go.Bar(
			x=weights,
			y=features,
			orientation="h",
			marker_color=colors,
			customdata=labels,
			text=[f"{w:.2f}" for w in weights],
			textposition="auto",
			hovertemplate="%{y}<br>Contribuție: %{x:.2f}<br>%{customdata}<extra></extra>",
			showlegend=False,
		)
	)

	fig.add_trace(go.Bar(x=[None], y=[None], marker_color="green", name="Contribuții pozitive"))
	fig.add_trace(go.Bar(x=[None], y=[None], marker_color="red", name="Contribuții negative"))

	fig.add_shape(type="line", x0=0, x1=0, y0=-0.5, y1=len(features) - 0.5, line=dict(color="black", width=2))

	fig.update_layout(
		title=f"Explicație LIME - predicție: {predicted_class} (probabilitate: {prediction_prob:.2f})",
		xaxis_title="Contribuție la predicție",
		yaxis_title="Caracteristici",
		yaxis=dict(autorange="reversed"),
		bargap=0.3,
		template="plotly_white",
		height=500,
		width=800,
		legend=dict(title="Tip contribuție", orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
	)

	return fig
