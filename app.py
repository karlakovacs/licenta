from tensorflow.python.keras.models import Sequential  # necesar pentru functionarea keras  # noqa: I001
import streamlit as st

from database import login_utilizator


st.set_page_config(page_title="Autentificare", page_icon="🔐", layout="centered")

if not st.user.is_logged_in:
	st.markdown(
		"<h1 style='font-size: 3em; font-weight: bold; text-align: center;'>Bun venit!</h1>",
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
	if st.button("Autentificare cu Google", type="primary"):
		st.login("google")

else:
	with st.spinner("Logare..."):
		id_google: str = st.user.sub
		st.session_state.id_utilizator = login_utilizator(id_google)
		st.switch_page("pages/0_acasa.py")
