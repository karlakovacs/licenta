import time

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import streamlit as st

from ml import get_model
from utils import nav_bar
from xai import get_dice_explainer


nav_bar()


@st.cache_data
def load_data():
	data = load_breast_cancer(as_frame=True)
	df = data.frame
	df["target"] = data.target
	return df, data.feature_names.tolist(), "target"


st.title("🔍 DiCE ML Counterfactual Explanations Demo")

df, feature_cols, target_col = load_data()

X = df[feature_cols]
y = df[target_col]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols)

X_train, X_test, y_train, y_test = train_test_split(X_scaled_df, y, test_size=0.2, random_state=42)

model_name = st.selectbox(
	"Alege un model de ML",
	[
		"Logistic Regression",
		"Linear Discriminant Analysis",
		"Quadratic Discriminant Analysis",
		"K-Nearest Neighbors",
		"Support Vector Classifier",
		"Decision Tree",
		"Random Forest",
		"Balanced Random Forest",
		"AdaBoost",
		"Gradient Boosting Classifier",
		"XGBoost",
		"LightGBM",
		"CatBoost",
		"Multilayer Perceptron",
	],
)
model = get_model(model_name)
model.fit(X_train, y_train)


time.sleep(5)

idx = st.slider("Selectează un exemplu de test", 0, len(X_test) - 1, 0)
idx = 0
input_data = X_test.iloc[idx : idx + 1]

st.subheader("📌 Exemplu Selectat")
st.write(input_data)

time.sleep(5)

prediction = model.predict(input_data)[0]
st.markdown(f"### 🔮 Predicția modelului `{model_name}`: `{prediction}`")

def highlight_positive_negative(val):
	if val > 0:
		return "background-color: lightgreen; color: black;"
	elif val < 0:
		return "background-color: salmon; color: black;"
	else:
		return ""


try:
	explainer = get_dice_explainer(model, X_train, y_train, target_col="target")
	time.sleep(5)

	with st.spinner("🔄 Generăm explicații contrafactuale..."):
		dice_exp = explainer.generate_counterfactuals(input_data, total_CFs=3, desired_class="opposite")

	time.sleep(5)
	st.subheader("🔁 Counterfactuals Suggerate")
	st.markdown("Modificări minime pentru a schimba predicția modelului:")

	time.sleep(5)
	cf_df = dice_exp.cf_examples_list[0].final_cfs_df[X_test.columns.tolist()]
	st.dataframe(cf_df)

	st.subheader("🔍 Diferențe față de exemplul original")
	time.sleep(5)
	diffs = cf_df - input_data.values
	time.sleep(5)
	st.write(diffs.style.applymap(highlight_positive_negative))

except Exception as e:
	st.error(f"Eroare la generarea explicațiilor pentru `{model_name}`: {e}")
