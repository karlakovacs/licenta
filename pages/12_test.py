import matplotlib.pyplot as plt
import shap
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import streamlit as st


# Load sample data
data = load_breast_cancer()
X = data["data"]
y = data["target"]
feature_names = data["feature_names"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train logistic regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# SHAP explainer
explainer = shap.LinearExplainer(model, X_train)
shap_values = explainer(X_test)

# Streamlit app
st.set_page_config(layout="wide", page_title="SHAP Test")
st.title("🔍 SHAP Test Page")
st.info("Model: Logistic Regression on Breast Cancer Dataset")

tab1, tab2, tab3 = st.tabs(["📊 Bar", "🎻 Violin", "💧 Waterfall"])

with tab1:
	st.subheader("SHAP Bar Plot")
	plt.clf()
	shap.plots.bar(shap_values, max_display=10, show=False)
	fig = plt.gcf()
	st.pyplot(fig)

with tab2:
	st.subheader("SHAP Violin Plot")
	plt.clf()
	shap.plots.violin(shap_values, max_display=10, show=False)
	fig = plt.gcf()
	st.pyplot(fig)

with tab3:
	st.subheader("SHAP Waterfall Plot (primul exemplu)")
	plt.clf()
	shap.plots.waterfall(shap_values[0], max_display=10, show=False)
	fig = plt.gcf()
	st.pyplot(fig)
