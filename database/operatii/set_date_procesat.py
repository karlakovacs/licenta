from datetime import datetime

from sqlalchemy import or_

from storage import *

from ..modele import SetDateBrut, SetDateProcesat
from ..utils import get_session


def create_set_date_procesat(id_utilizator: int, id_set_date: int, configuratie: dict, df: pd.DataFrame):
	db = get_session()

	set_brut = (
		db.query(SetDateBrut)
		.filter(
			SetDateBrut.id == id_set_date,
			or_(SetDateBrut.id_utilizator == id_utilizator, SetDateBrut.id_utilizator == None),
		)
		.first()
	)

	if not set_brut:
		raise ValueError("Setul de date brut nu există sau nu aparține utilizatorului.")

	data = datetime.now()
	timestamp = data.strftime("%Y-%m-%d-%H-%M-%S")
	noua_denumire = f"{set_brut.denumire}_procesat_{timestamp}"

	url = upload_dataset_to_storage(df, id_utilizator, noua_denumire)

	set_date_procesat = SetDateProcesat(
		id_set_date=id_set_date,
		denumire=noua_denumire,
		configuratie=configuratie,
		url=url,
		data_procesare=data,
	)

	db.add(set_date_procesat)
	db.commit()
	db.refresh(set_date_procesat)

	return set_date_procesat.id


def get_seturi_date_procesate(id_set_date_brut: int) -> list:
	db = get_session()

	lista = (
		db.query(SetDateProcesat)
		.filter(SetDateProcesat.id_set_date == id_set_date_brut)
		.order_by(SetDateProcesat.data_procesare.desc())
		.all()
	)

	return lista

def get_seturi_date_procesate_utilizator(id_utilizator: int) -> list:
	db = get_session()

	lista = (
		db.query(SetDateProcesat)
		.join(SetDateBrut, SetDateProcesat.set_date_brut)
		.filter(SetDateBrut.id_utilizator == id_utilizator)
		.order_by(SetDateProcesat.data_procesare.desc())
		.all()
	)

	return lista

def delete_set_date_procesat(id_set_date_procesat: int) -> str:
	db = get_session()

	set_date_procesat = db.query(SetDateProcesat).filter_by(id=id_set_date_procesat).first()

	if set_date_procesat is None:
		return False, "Setul de date nu există sau nu aparține utilizatorului"

	delete_dataset_from_storage(set_date_procesat.url)

	db.delete(set_date_procesat)
	db.commit()

	return True, "Setul de date a fost șters"


def get_tinta_by_id_set_date_procesat(id_set_date_procesat: int) -> str | None:
	db = get_session()

	set_procesat = (
		db.query(SetDateProcesat).filter_by(id=id_set_date_procesat).join(SetDateProcesat.set_date_brut).first()
	)

	if set_procesat is None or set_procesat.set_date_brut is None:
		return None

	return set_procesat.set_date_brut.tinta


def get_sursa_by_id_set_date_procesat(id_set_date_procesat: int) -> str | None:
	db = get_session()

	set_procesat = (
		db.query(SetDateProcesat)
		.filter_by(id=id_set_date_procesat)
		.join(SetDateProcesat.set_date_brut)
		.join(SetDateBrut.sursa_date)
		.first()
	)

	if set_procesat is None or set_procesat.set_date_brut is None:
		return None

	return set_procesat.set_date_brut.sursa_date.denumire if set_procesat.set_date_brut.sursa_date else None
