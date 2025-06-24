import streamlit as st

from dataset import citire_date_temp
from ui import *
from xai import ui_test


initializare_pagina("XAI", "wide", "Explainable AI", {"xai_test": {}})


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
@require_trained_models
def main():
	modele_antrenate = st.session_state.get("modele_antrenate", {})
	X_train, X_test, y_train = (
		citire_date_temp("X_train"),
		citire_date_temp("X_test"),
		citire_date_temp("y_train"),
	)
	ui_test(modele_antrenate, X_train, y_train, X_test)


if __name__ == "__main__":
	main()
