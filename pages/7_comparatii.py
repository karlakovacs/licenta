import streamlit as st

from ml import creare_df_comparatii, grafic_comparativ
from ui import (
	initializare_pagina,
	require_auth,
	require_processed_dataset,
	require_selected_dataset,
	require_selected_models,
	require_trained_models,
)


initializare_pagina("Comparații", "wide", "Compararea performanței modelelor", {"comparatii_modele": {}})


@require_auth
@require_selected_dataset
@require_processed_dataset
@require_selected_models
@require_trained_models
def main():
	rezultate_modele = st.session_state.get("rezultate_modele", None)
	date = st.session_state["comparatii_modele"]
	if not date:
		date["df_comparatii"] = creare_df_comparatii(rezultate_modele)
		date["grafic"] = grafic_comparativ(date["df_comparatii"])

	st.header(
		"Modele și metrici",
		help="Afișează toate modelele antrenate împreună cu valorile fiecărei metrici de performanță.",
	)
	st.dataframe(date["df_comparatii"], hide_index=True, use_container_width=True)
	st.header("Grafic comparativ", help="Compară performanțele modelelor pentru fiecare metrică prin diagrame bară.")
	st.plotly_chart(date["grafic"], use_container_width=True)


if __name__ == "__main__":
	main()
