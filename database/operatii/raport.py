from datetime import datetime, timezone

from ..modele import Raport
from ..utils import get_session


def create_raport(id_set_date_procesat, url: str):
	db = get_session()

	raport = Raport(
		id_set_date_procesat=id_set_date_procesat,
		url=url,
		data_generare=datetime.now(timezone.utc),
	)
	db.add(raport)
	db.commit()
	db.refresh(raport)
	return raport.id


def get_rapoarte(id_set_date_procesat: int) -> list:
	db = get_session()
	lista = (
		db.query(Raport)
		.filter(Raport.id_set_date_procesat == id_set_date_procesat)
		.order_by(Raport.data_generare.desc())
		.all()
	)
	return lista


def delete_raport(id_raport: int) -> str:
	db = get_session()

	raport = db.query(Raport).filter_by(id=id_raport).first()

	if raport is None:
		return False, "Raportul nu există sau nu aparține utilizatorului"

	db.delete(raport)
	db.commit()

	return True, "Raportul a fost șters"
