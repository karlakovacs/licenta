from datetime import datetime

from storage import delete_dataset_from_storage, delete_model_from_storage, delete_report_from_storage

from ..modele import Utilizator
from ..utils import get_auth0, get_session


def login(id_auth0: str) -> int:
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_auth0 == id_auth0).first()
	if not utilizator:
		utilizator = Utilizator(id_auth0=id_auth0)
		db.add(utilizator)
	else:
		utilizator.data_ultima_conectare = datetime.now()
	db.commit()
	db.refresh(utilizator)

	return utilizator.id


def get_id_utilizator(id_auth0: str) -> int:
	if id_auth0 is None:
		return None

	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_auth0 == id_auth0).first()
	return utilizator.id


def delete_utilizator(id_utilizator: int):
	auth0 = get_auth0()
	db = get_session()

	utilizator = db.query(Utilizator).filter_by(id=id_utilizator).first()
	if utilizator is None:
		return False, "Utilizatorul nu există."

	id_auth0 = utilizator.id_auth0

	for set_b in utilizator.seturi_date:
		delete_dataset_from_storage(set_b.url)

		for set_p in set_b.seturi_procesate:
			for model in set_p.modele:
				delete_model_from_storage(model.url)

			delete_dataset_from_storage(set_p.url)
			db.delete(set_p)

		db.delete(set_b)

	for raport in utilizator.rapoarte:
		delete_report_from_storage(id_utilizator, raport.id)
		db.delete(raport)

	db.delete(utilizator)
	db.commit()

	auth0.users.delete(id_auth0)

	return True, "Utilizatorul a fost șters."
