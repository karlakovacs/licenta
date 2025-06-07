from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st
from supabase import create_client

from database.modele import Raport, SetDate, Utilizator


DATABASE_URL = st.secrets.supabase.DATABASE_URL


@st.cache_resource
def get_engine():
	return create_engine(DATABASE_URL)


def get_session():
	engine = get_engine()
	Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
	return Session()


def get_client():
	SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
	SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY
	supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
	return supabase


def sign_up_email(nume, email, parola, confirmare):
	db = get_session()
	supabase = get_client()
	email = email.strip()

	if parola != confirmare:
		return False, "Parolele nu coincid."

	try:
		result = supabase.auth.sign_up({"email": email, "password": parola})
		user = result.user

		if user:
			utilizator = db.query(Utilizator).filter_by(id_supabase=user.id).first()
			if not utilizator:
				utilizator = Utilizator(
					id_supabase=user.id, email=email, nume=nume, data_creare=datetime.now(timezone.utc)
				)
				db.add(utilizator)
				db.commit()

			return True, "Cont creat. Verifică emailul."
		else:
			return False, "Eroare la înregistrare."

	except Exception as e:
		return False, f"Eroare: {e}"


def login_email(email, parola):
	db = get_session()
	supabase = get_client()
	email = email.strip()

	try:
		result = supabase.auth.sign_in_with_password({"email": email, "password": parola})
		user = result.user

		if user:
			utilizator = db.query(Utilizator).filter_by(id_supabase=user.id).first()
			if not utilizator:
				utilizator = Utilizator(id_supabase=user.id, email=user.email, data_creare=datetime.now(timezone.utc))
				db.add(utilizator)

			utilizator.data_ultima_conectare = datetime.now(timezone.utc)
			db.commit()
			db.refresh(utilizator)
			return True, f"Salut, {utilizator.nume}", utilizator.id

		else:
			return False, "Autentificare eșuată."

	except Exception as e:
		return False, f"Eroare: {e}"


def login_google(id_google: str) -> int:
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_google == id_google).first()
	if not utilizator:
		utilizator = Utilizator(id_google=id_google)
		db.add(utilizator)
	else:
		utilizator.data_ultima_conectare = datetime.now(timezone.utc)
	db.commit()
	db.refresh(utilizator)

	return utilizator.id


def get_utilizator(id_google):
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_google == id_google).first()
	return utilizator.id


def creare_set_date(id_utilizator: int, denumire: str, sursa: str, url: str, tinta: str) -> SetDate:
	db = get_session()

	set_date = SetDate(
		id_utilizator=id_utilizator,
		denumire=denumire,
		sursa=sursa,
		url=url,
		tinta=tinta,
		data_creare=datetime.now(timezone.utc),
	)
	db.add(set_date)
	db.commit()
	db.refresh(set_date)
	return set_date.id


def get_seturi_date_utilizator(id_utilizator: int) -> list:
	db = get_session()
	lista = db.query(SetDate).filter(SetDate.id_utilizator == id_utilizator).order_by(SetDate.data_creare.desc()).all()
	return lista


def modificare_set_date(
	id_utilizator: int, id_set_date: int, denumire: str = None, tinta: str = None
) -> tuple[bool, str]:
	db = get_session()

	if denumire is None and tinta is None:
		return False, "Nimic de modificat"

	set_date = db.query(SetDate).filter_by(id=id_set_date, id_utilizator=id_utilizator).first()

	if set_date is None:
		return False, "Setul de date nu există sau nu aparține utilizatorului"

	if denumire is not None:
		set_date.denumire = denumire
	if tinta is not None:
		set_date.tinta = tinta
	set_date.data_actualizare = datetime.now(timezone.utc)
	db.commit()

	return True, "Setul de date a fost modificat"


def stergere_set_date(id_utilizator: int, id_set_date: int) -> str:
	db = get_session()

	set_date = db.query(SetDate).filter_by(id=id_set_date, id_utilizator=id_utilizator).first()

	if set_date is None:
		return False, "Setul de date nu există sau nu aparține utilizatorului"

	db.delete(set_date)
	db.commit()

	return True, "Setul de date a fost șters"


def verificare_denumire_set_date(id_utilizator: int, denumire: str) -> bool:
	db = get_session()
	return (
		db.query(SetDate).filter(SetDate.id_utilizator == id_utilizator, SetDate.denumire == denumire).first()
		is not None
	)


def creare_raport(id_utilizator: int, url: str):
	db = get_session()

	raport = Raport(
		id_utilizator=id_utilizator,
		url=url,
		data_generare=datetime.now(timezone.utc),
	)
	db.add(raport)
	db.commit()
	db.refresh(raport)
	return raport.id


def get_rapoarte_utilizator(id_utilizator: int) -> list:
	db = get_session()
	lista = db.query(Raport).filter(Raport.id_utilizator == id_utilizator).order_by(Raport.data_generare.desc()).all()
	return lista


def stergere_raport(id_utilizator: int, id_raport: int) -> str:
	db = get_session()

	raport = db.query(Raport).filter_by(id=id_raport, id_utilizator=id_utilizator).first()

	if raport is None:
		return False, "Raportul nu există sau nu aparține utilizatorului"

	db.delete(raport)
	db.commit()

	return True, "Raportul a fost șters"
