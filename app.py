from keras.api.models import Sequential  # necesar pentru functionarea keras  # noqa: I001
import streamlit as st
from database import login
from ui import configurare_pagina


configurare_pagina("Auth", "wide")


def afisare_sectiune(i: int):
	st.image(f"assets/landing-page/{i}.png")


if not st.user.is_logged_in:
	st.sidebar.image(f"assets/logo/logo-text.png", use_container_width=True)
	if st.sidebar.button("**Autentificare**", type="primary", use_container_width=True):
		st.login("auth0")

	col1, col2 = st.columns([3, 1])
	with col1:
		st.title("Bun venit în platforma :red-background[FlagML]!")

		st.write(
			"""
			**FlagML 🏁** este o aplicație educațională interactivă care oferă o experiență completă în :red-background[**detectarea fraudei bancare 🚨**] folosind învățarea automată (*Machine Learning*) și interpretabilitatea modelelor (*Explainable AI*).
			
			**Scopul principal al aplicației** este aplicarea tehnicilor moderne de ML în contextul combaterii fraudei.

			Fie că ești student, expert sau pasionat de date, **FlagML** îți oferă tot ce ai nevoie pentru a realiza un proiect ML complet: de la date brute până la modele interpretabile și rapoarte clare.
			"""
		)

	with col2:
		st.write("\n\n")
		st.image("assets/landing-page/0.jpg", width=400)

	st.divider()

	st.header("Funcționalitățile aplicației")

	functii = [
		{
			"titlu": "Încărcarea datelor",
			"text": "Importă rapid date proprii sau seturi predefinite pentru detectarea fraudei.",
			"img": "assets/landing-page/1.png",
		},
		{
			"titlu": "Analiza datelor",
			"text": "Vizualizează distribuții, corelații și alte insight-uri esențiale.",
			"img": "assets/landing-page/2.png",
		},
		{
			"titlu": "Antrenarea modelelor ML",
			"text": "Testează automat 14 algoritmi de clasificare binară.",
			"img": "assets/landing-page/3.png",
		},
		{
			"titlu": "Evaluarea algoritmilor",
			"text": "Folosește metrici și grafice pentru a interpreta rezultatele.",
			"img": "assets/landing-page/4.png",
		},
		{
			"titlu": "Explainable AI (XAI)",
			"text": "Înțelege de ce un model clasifică o tranzacție ca frauduloasă.",
			"img": "assets/landing-page/5.png",
		},
		{
			"titlu": "Exportul datelor",
			"text": "Descarcă date, modele antrenate și rapoarte HTML.",
			"img": "assets/landing-page/6.png",
		},
	]

	cols = st.columns(6)
	for col, functie in zip(cols, functii):
		with col:
			st.image(functie["img"], use_container_width=True)
			st.write(f"**{functie['titlu']}**")
			st.write(f"{functie['text']}", unsafe_allow_html=True)

else:
	with st.spinner("Se face logarea..."):
		id_auth0 = st.user.sub
		st.session_state.id_utilizator = login(id_auth0)
		st.switch_page("pages/0_acasa.py")
