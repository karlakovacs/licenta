import streamlit as st

from ml import creare_df_metrici, grafic_comparativ, interpretare_comparatii
from ui import *


initializare_pagina("Comparații", "wide", "Compararea performanței modelelor", {"comparatii_modele", {}})


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
@require_trained_models
def main():
	rezultate_modele = st.session_state.get("rezultate_modele", None)
	date = st.session_state["comparatii_modele"]
	if not date:
		date["df_metrici"] = creare_df_metrici(rezultate_modele)
		date["grafic_comparativ"] = grafic_comparativ(st.session_state.df_metrici)
		date["interpretare"] = interpretare_comparatii(st.session_state.df_metrici)

	st.dataframe(date["df_metrici"])
	st.plotly_chart(date["grafic_comparativ"], use_container_width=False)
	st.header("Intepretare")
	st.write(date["interpretare"])


if __name__ == "__main__":
	main()
