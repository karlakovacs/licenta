from datetime import datetime

import pandas as pd
from sqlalchemy.orm import joinedload

from storage import delete_dataset_from_storage, upload_dataset_to_storage

from .set_date_procesat import delete_set_date_procesat, get_seturi_date_procesate
from ..modele import SetDateBrut, SursaDate
from ..utils import get_session


def create_set_date_brut(id_utilizator: int, sursa: str, denumire: str, tinta: str, df: pd.DataFrame):
	db = get_session()

	url = upload_dataset_to_storage(df, id_utilizator, denumire)

	surse_date = db.query(SursaDate).all()
	sursa_to_id = {s.denumire: s.id for s in surse_date}
	id_sursa = sursa_to_id.get(sursa)

	if id_sursa is None:
		print(f"Sursa '{sursa}' nu există în tabela 'surse_date'.")
		return None

	set_date = SetDateBrut(
		id_utilizator=id_utilizator,
		id_sursa=id_sursa,
		denumire=denumire,
		tinta=tinta,
		url=url,
		data_creare=datetime.now(),
	)

	db.add(set_date)
	db.commit()
	db.refresh(set_date)

	return set_date.id


def get_seturi_date_brute(id_utilizator: int) -> list:
	db = get_session()

	lista = (
		db.query(SetDateBrut)
		.options(joinedload(SetDateBrut.sursa_date))
		.filter(SetDateBrut.id_utilizator == id_utilizator)
		.order_by(SetDateBrut.data_creare.desc())
		.all()
	)

	return lista


def get_seturi_date_predefinite() -> list:
	db = get_session()
	lista = db.query(SetDateBrut).filter(SetDateBrut.id_sursa == 3).order_by(SetDateBrut.data_creare.asc()).all()
	return lista


def update_set_date_brut(
	id_utilizator: int, id_set_date: int, denumire: str = None, tinta: str = None
) -> tuple[bool, str]:
	db = get_session()

	if denumire is None and tinta is None:
		return False, "Nimic de modificat"

	set_date = db.query(SetDateBrut).filter_by(id=id_set_date, id_utilizator=id_utilizator).first()

	if set_date is None:
		return False, "Setul de date nu există sau nu aparține utilizatorului"

	if denumire is not None:
		set_date.denumire = denumire

	if tinta is not None:
		set_date.tinta = tinta

	set_date.data_actualizare = datetime.now()
	db.commit()

	return True, "Setul de date a fost modificat"


def delete_set_date_brut(id_utilizator: int, id_set_date: int) -> tuple[bool, str]:
	db = get_session()

	set_date = db.query(SetDateBrut).filter_by(id=id_set_date, id_utilizator=id_utilizator).first()

	if set_date is None:
		return False, "Setul de date nu există sau nu aparține utilizatorului."

	succes_storage, mesaj_storage = delete_dataset_from_storage(set_date.url)
	if not succes_storage:
		return succes_storage, mesaj_storage

	seturi_date_procesate = get_seturi_date_procesate(id_set_date)
	for set_procesat in seturi_date_procesate:
		succes_proc, mesaj_proc = delete_set_date_procesat(id_set_date_procesat=set_procesat.id)
		if not succes_proc:
			return succes_proc, f"Eroare la ștergerea setului procesat {set_procesat.id}: {mesaj_proc}"

	db.delete(set_date)
	db.commit()

	return True, "Setul de date a fost șters cu succes."


def check_denumire_set_date_brut(id_utilizator: int, denumire: str) -> bool:
	db = get_session()
	return (
		db.query(SetDateBrut)
		.filter(SetDateBrut.id_utilizator == id_utilizator, SetDateBrut.denumire == denumire)
		.first()
		is not None
	)


def get_tinta_by_id_set_date_brut(id_set_date_brut: int) -> str | None:
	db = get_session()

	set_date = db.query(SetDateBrut).filter_by(id=id_set_date_brut).first()

	if set_date is None:
		return None

	return set_date.tinta


def get_sursa_by_id_set_date_brut(id_set_date_brut: int) -> str | None:
	db = get_session()

	set_brut = db.query(SetDateBrut).filter_by(id=id_set_date_brut).first()
	if set_brut is None:
		return None

	return set_brut.sursa_date.denumire if set_brut.sursa_date else None
