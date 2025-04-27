# import pandas as pd
# from sklearn.datasets import load_breast_cancer
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# import streamlit as st

# from utils import nav_bar


# nav_bar()


# @st.cache_data
# def load_data():
# 	data = load_breast_cancer(as_frame=True)
# 	df = data.frame
# 	df["target"] = data.target
# 	return df, data.feature_names.tolist(), "target"


# st.title("Test")

# df, feature_cols, target_col = load_data()
# X = df[feature_cols]
# y = df[target_col]

# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
# X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols)

# X_train, X_test, y_train, y_test = train_test_split(X_scaled_df, y, test_size=0.2, random_state=42)

# model_name = st.selectbox(
# 	"Alege un model de ML",
# 	[
# 		"Logistic Regression",
# 		"Linear Discriminant Analysis",
# 		"Quadratic Discriminant Analysis",
# 		"K-Nearest Neighbors",
# 		"Support Vector Classifier",
# 		"Decision Tree",
# 		"Random Forest",
# 		"Balanced Random Forest",
# 		"AdaBoost",
# 		"Gradient Boosting Classifier",
# 		"XGBoost",
# 		"LightGBM",
# 		"CatBoost",
# 		"Multilayer Perceptron",
# 	],
# )
