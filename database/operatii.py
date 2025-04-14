from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker
import streamlit as st

from database.modele import *


DATABASE_URL = st.secrets.supabase.DATABASE_URL


@st.cache_resource
def get_session():
	engine = create_engine(DATABASE_URL)
	Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
	return Session()


def login_utilizator(user_info):
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.google_id == user_info["id"]).first()
	if not utilizator:
		utilizator = Utilizator(google_id=user_info["id"], email=user_info["email"])
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


def creare_preprocesare(id_utilizator: int, valori: dict):
	db = get_session()
	try:
		preprocesare = Preprocesare(
			id_utilizator=id_utilizator,
			id_set_date=valori.get("id_set_date"),
			optiune_selectie=valori.get("optiune_selectie"),
			nr_variabile=valori.get("nr_variabile"),
			optiune_dezechilibru=valori.get("optiune_dezechilibru"),
			optiune_scalare=valori.get("optiune_scalare"),
			dimensiune_test=valori.get("dimensiune_test"),
			stratificat=valori.get("stratificat"),
		)

		db.add(preprocesare)
		db.commit()
		db.refresh(preprocesare)
		st.write(preprocesare.__dict__)

		return preprocesare.id
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()


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


def creare_rulare(
	id_preprocesare: int,
	model: str,
	metrici: list,
	timp_executie: float,
	hiperparametri: dict = None,
):
	db = get_session()
	try:
		metrici_dict = dict(zip(DENUMIRI_METRICI, metrici))
		rulare = Rulare(
			id_preprocesare=id_preprocesare,
			model=model,
			metrici=metrici_dict,
			timp_executie=timp_executie,
			hiperparametri=hiperparametri if hiperparametri else {},
		)

		db.add(rulare)
		db.commit()
		db.refresh(rulare)
		return rulare.id
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()


def get_preprocesari_rulari_grafice(id_utilizator: int) -> list:
	db = get_session()
	try:
		preprocesari = (
			db.query(Preprocesare)
			.filter(Preprocesare.id_utilizator == id_utilizator)
			.options(joinedload(Preprocesare.rulari).joinedload(Rulare.grafice))
			.all()
		)

		rezultat = []
		for preprocesare in preprocesari:
			preprocesare_dict = {
				"id_preprocesare": preprocesare.id,
				"set_date": preprocesare.set_date,
				"optiune_selectie": preprocesare.optiune_selectie,
				"nr_variabile": preprocesare.nr_variabile,
				"optiune_dezechilibru": preprocesare.optiune_dezechilibru,
				"optiune_scalare": preprocesare.optiune_scalare,
				"dimensiune_test": preprocesare.dimensiune_test,
				"stratificat": preprocesare.stratificat,
				"created_at": preprocesare.created_at,
				"rulari": [],
			}

			for rulare in preprocesare.rulari:
				rulare_dict = {
					"id_rulare": rulare.id,
					"model": rulare.model,
					"metrici": rulare.metrici,
					"timp_executie": rulare.timp_executie,
					"hiperparametri": rulare.hiperparametri,
					"created_at": rulare.created_at,
					"grafice": [],
				}

				for grafic in rulare.grafice:
					rulare_dict["grafice"].append({"id_grafic": grafic.id, "sursa": grafic.sursa, "url": grafic.url})

				preprocesare_dict["rulari"].append(rulare_dict)

			rezultat.append(preprocesare_dict)

		return rezultat
	except Exception as e:
		raise e
	finally:
		db.close()
