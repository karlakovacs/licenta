from tensorflow.python.keras.models import Sequential  # necesar pentru functionarea keras  # noqa: I001
import streamlit as st
from database import login_email, login_google, sign_up_email


st.set_page_config(page_title="Autentificare", page_icon="assets/logo.png", layout="wide")

if not st.user.is_logged_in:
	col1, col2 = st.columns([2, 1])

	with col1:
		st.image("assets/logo.png", width=100)
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

	with col2:
		st.title("Autentificare")

		tab = st.tabs(["Login", "Sign Up"])

		with tab[0]:
			st.subheader("Login")
			email = st.text_input("Email", key="email_login")
			parola = st.text_input("Parolă", type="password", key="password_login")
			if st.button("Login"):
				success, msg, id_utilizator = login_email(email, parola)
				if success:
					st.success(msg)
					st.session_state.id_utilizator = id_utilizator
					st.switch_page("pages/0_acasa.py")
				else:
					st.error(msg)

		with tab[1]:
			st.subheader("Creare cont nou")
			nume = st.text_input("Nume", key="name_sign_up")
			email = st.text_input("Email", key="email_sign_up")
			parola = st.text_input("Parolă", type="password", key="password_sign_up")
			confirmare = st.text_input("Confirmă parola", type="password", key="confirm_password_sign_up")
			if st.button("Creează cont"):
				success, msg = sign_up_email(nume, email, parola, confirmare)
				if success:
					st.success(msg)
				else:
					st.error(msg)

		st.divider()

		if st.button("Autentificare cu Google", type="primary"):
			st.login("google")

else:
	with st.spinner("Se face logarea..."):
		id_google = st.user.sub
		st.session_state.id_utilizator = login_google(id_google)
		st.switch_page("pages/0_acasa.py")
