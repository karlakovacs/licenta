from storage import delete_report_from_storage

from ..modele import Raport
from ..utils import get_session


def create_raport(id_utilizator, url: str, data_generare: str):
	db = get_session()

	raport = Raport(
		id_utilizator=id_utilizator,
		url=url,
		data_generare=data_generare,
	)
	db.add(raport)
	db.commit()
	db.refresh(raport)
	return raport.id


def get_rapoarte(id_utilizator: int) -> list:
	db = get_session()
	lista = (
		db.query(Raport)
		.filter(Raport.id_utilizator == id_utilizator)
		.order_by(Raport.data_generare.desc())
		.all()
	)
	return lista


def delete_raport(id_utilizator: int, id_raport: int):
	db = get_session()

	raport = db.query(Raport).filter_by(id=id_raport, id_utilizator=id_utilizator).first()

	if raport is None:
		return False, "Raportul nu există sau nu aparține utilizatorului"
	
	succes_storage, mesaj_storage = delete_report_from_storage(id_utilizator, raport.id)
	if not succes_storage:
		return succes_storage, mesaj_storage

	db.delete(raport)
	db.commit()

	return True, "Raportul a fost șters"
