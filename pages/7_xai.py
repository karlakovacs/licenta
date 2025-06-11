import streamlit as st

from dataset import citire_date_temp
from utils import nav_bar
from xai import ui_test


st.set_page_config(layout="wide", page_title="FlagML | XAI", page_icon="assets/logo.png")
nav_bar()
st.title("Explainable AI")


modele_antrenate = st.session_state.get("modele_antrenate", {})
X_train, X_test, y_train = (
	citire_date_temp("X_train"),
	citire_date_temp("X_test"),
	citire_date_temp("y_train"),
)

if not modele_antrenate:
	st.warning("Antrenează modelele mai întâi.")

else:
	ui_test(modele_antrenate, X_train, y_train, X_test)
