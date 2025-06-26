import streamlit as st

from ui import *


initializare_pagina("Acasă", "centered", "Acasă")


@require_auth
def main():
	st.write(
		"""
		FlagML este o aplicație dedicată detectării fraudei bancare, utilizând metode moderne de ML.

		Fiecare tranzacție bancară poate fi clasificată ca frauduloasă sau legitimă, ceea ce face ca această sarcină să fie una tipică de clasificare binară.

		Prin această aplicație, utilizatorii pot parcurge întregul flux de lucru ML: de la încărcarea datelor și analiza exploratorie, până la antrenarea modelelor, interpretarea deciziilor și generarea de rapoarte automate.
		"""
	)

	col1, col2 = st.columns([1, 2])

	with col1:
		if st.button("✨ Începe o analiză nouă", type="primary"):
			st.session_state.clear()
			st.switch_page("pages/1_dataset.py")

	with col2:
		if st.button("🗂️ Vizualizează rapoartele și modelele personale", type="secondary"):
			st.switch_page("pages/11_date.py")

	st.image("assets/home/ai.png")


if __name__ == "__main__":
	main()
