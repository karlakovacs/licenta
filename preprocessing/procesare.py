from imblearn.over_sampling import ADASYN, SMOTE
from imblearn.under_sampling import RandomUnderSampler
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
import streamlit as st

from database import *
from utils import *


def procesare_dataset(
	df: pd.DataFrame,
	tinta,
	optiune_selectie,
	nr_variabile,
	optiune_dezechilibru,
	optiune_scalare,
	dimensiune_test,
	stratificat,
):
	X, y = df.drop(columns=[tinta]), df[tinta].values.ravel()

	if optiune_selectie == "Testul ANOVA":
		selector = SelectKBest(f_classif, k=nr_variabile)
		X_selected = selector.fit_transform(X, y)
		variabile_selectate = X.columns[selector.get_support()]
		X = pd.DataFrame(X_selected, columns=variabile_selectate)
	elif optiune_selectie == "...":
		mi_scores = mutual_info_classif(X, y)
		mi_df = pd.DataFrame({"Variabilă": X.columns, "Scor MI": mi_scores})
		mi_df = mi_df.sort_values(by="Scor MI", ascending=False)

	if optiune_dezechilibru == "Undersampling":
		rus = RandomUnderSampler(sampling_strategy="majority", random_state=42)
		X, y = rus.fit_resample(X, y)
	elif optiune_dezechilibru == "Oversampling":
		smote = SMOTE(sampling_strategy="minority", random_state=42)
		X, y = smote.fit_resample(X, y)
	elif optiune_dezechilibru == "ADASYN":
		adasyn = ADASYN(sampling_strategy="minority", random_state=42)
		X, y = adasyn.fit_resample(X, y)

	scaler = None
	if optiune_scalare == "StandardScaler":
		scaler = StandardScaler()
	elif optiune_scalare == "MinMaxScaler":
		scaler = MinMaxScaler()
	elif optiune_scalare == "RobustScaler":
		scaler = RobustScaler()
	if scaler is not None:
		X_scaled = scaler.fit_transform(X)
		X = pd.DataFrame(X_scaled, columns=X.columns)

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=dimensiune_test, stratify=y if stratificat else None, random_state=42)

	X_train = pd.DataFrame(X_train, columns=X.columns).reset_index(drop=True)
	X_test = pd.DataFrame(X_test, columns=X.columns).reset_index(drop=True)
	y_train = pd.Series(y_train, name=tinta).reset_index(drop=True)
	y_test = pd.Series(y_test, name=tinta).reset_index(drop=True)
	for name, data in zip(["X_train", "X_test", "y_train", "y_test"], [X_train, X_test, y_train, y_test]):
		salvare_date_temp(data, name)
	setari_preprocesare = {
		"set_date": st.session_state.nume_dataset,
		"optiune_selectie": optiune_selectie,
		"nr_variabile": nr_variabile,
		"optiune_dezechilibru": optiune_dezechilibru,
		"optiune_scalare": optiune_scalare,
		"dimensiune_test": dimensiune_test,
		"stratificat": stratificat,
	}

	id_utilizator = st.session_state.id_utilizator

	st.session_state.id_preprocesare = creare_preprocesare(id_utilizator, setari_preprocesare)
	st.success("Done!")

	return setari_preprocesare
