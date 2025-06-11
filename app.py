from keras.api.models import Sequential  # necesar pentru functionarea keras  # noqa: I001
import streamlit as st
from database import login


st.set_page_config(layout="wide", page_title="FlagML | Auth", page_icon="assets/logo.png")

if not st.user.is_logged_in:
	col1, col2 = st.columns([2, 1])

	with col1:
		st.image("assets/logo-text.png", width=100)
		st.markdown(
			"<h1 style='text-align: center;'>Bun venit!</h1>",
			unsafe_allow_html=True,
		)

		st.markdown(
			"""
		Această aplicație educațională este concepută pentru a ajuta utilizatorii să înțeleagă și să exerseze clasificarea binară, adică probleme în care rezultatul are doar două valori posibile (de exemplu, o tranzacție bancară poate fi frauduloasă sau legitimă).

		Scopul principal este prezentarea fluxului complet al unui proiect de machine learning, de la încărcarea datelor până la antrenarea, evaluarea și interpretarea modelelor predictive. Aplicația oferă suport pentru:
		
		- Încărcarea unui dataset propriu (local sau de pe Kaggle) sau utilizarea unor seturi de date reale referitoare la detectarea fraudei bancare;
		- Analiza exploratorie a datelor pentru a înțelege setul de date;
		- Rularea a 14 algoritmi populari pentru clasificare binară;
		- Vizualizarea performanței modelelor prin metrici clasice și grafice utile;
		- Explainable AI (XAI) pentru a analiza modul în care modelele de machine learning iau decizii;
		- Generarea de rapoarte în format interactiv (HTML) sau clasic (PDF).
		"""
		)

	with col2:
		if st.button("Autentificare", type="primary"):
			st.login("auth0")

else:
	with st.spinner("Se face logarea..."):
		id_auth0 = st.user.sub
		st.session_state.id_utilizator = login(id_auth0)
		st.switch_page("pages/0_acasa.py")
