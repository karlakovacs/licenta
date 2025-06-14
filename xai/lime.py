import lime
from lime.explanation import Explanation
from lime.lime_tabular import LimeTabularExplainer
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def get_lime_explainer(model, X_train: pd.DataFrame, metadate: dict) -> LimeTabularExplainer:
	try:
		is_mlp = hasattr(model, "layers")
		variabile_categoriale_nume = metadate["variabile_categoriale"]
		variabile_categoriale = (
			[i for i, col in enumerate(X_train.columns) if col in variabile_categoriale_nume] if not is_mlp else []
		)

		explainer = LimeTabularExplainer(
			training_data=X_train.to_numpy(),
			feature_names=X_train.columns,
			class_names=["False", "True"],
			categorical_features=variabile_categoriale,
			mode="classification",
		)
		return explainer

	except Exception as e:
		return None


def get_explanation(model, explainer: LimeTabularExplainer, X_explicat: pd.DataFrame) -> Explanation | None:
	try:
		instance = X_explicat.values.flatten()

		if hasattr(model, "predict_proba"):
			predict_fn = model.predict_proba

		else:  # keras-style predict

			def predict_fn(X):
				probs = model.predict(X)
				return np.hstack([1 - probs, probs])

		explanation = explainer.explain_instance(data_row=instance, predict_fn=predict_fn)
		return explanation

	except Exception as e:
		return None


def lime_plot(explanation: Explanation) -> go.Figure:
	lime_results = sorted(explanation.as_list(), key=lambda x: abs(x[1]), reverse=True)

	features = [desc for desc, _ in lime_results]
	weights = [weight for _, weight in lime_results]
	colors = ["green" if w > 0 else "red" for w in weights]
	labels = ["Contribuții pozitive" if w > 0 else "Contribuții negative" for w in weights]

	class_names = explanation.class_names
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
