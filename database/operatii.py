from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st

from database.modele import *


DATABASE_URL = st.secrets.supabase.DATABASE_URL


@st.cache_resource
def get_engine():
	return create_engine(DATABASE_URL)


def get_session():
	engine = get_engine()
	Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
	return Session()


def login_utilizator(user_info):
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_google == user_info["id"]).first()
	if not utilizator:
		utilizator = Utilizator(id_google=user_info["id"], email=user_info["email"])
		db.add(utilizator)
	else:
		utilizator.last_login = datetime.now(timezone.utc)
	db.commit()
	db.refresh(utilizator)

	return utilizator.id


def get_utilizator(id_google):
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_google == id_google).first()
	return utilizator.id
	# st.write(utilizator.__dict__)


def creare_set_date(
	id_utilizator: int,
	denumire: str,
	sursa: str,
	url: str,
) -> SetDate:
	db = get_session()

	set_date = SetDate(
		id_utilizator=id_utilizator, denumire=denumire, sursa=sursa, url=url, data_creare=datetime.now(timezone.utc)
	)
	db.add(set_date)
	db.commit()
	db.refresh(set_date)
	return set_date.id


def get_seturi_date_utilizator(id_utilizator: int):
	db = get_session()
	return db.query(SetDate).filter(SetDate.id_utilizator == id_utilizator).order_by(SetDate.data_creare.desc()).all()


DENUMIRI_METRICI = [
	"accuracy",
	"recall",
	"precision",
	"f1",
	"roc_auc",
	"avg_precision",
	"bcr",
	"kappa",
	"mcc",
	"gm",
	"tpr",
	"tnr",
	"fpr",
	"fnr",
]
