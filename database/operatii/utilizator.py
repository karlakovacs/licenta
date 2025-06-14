from datetime import datetime, timezone

from ..modele import Utilizator
from ..utils import get_session


def login(id_auth0: str) -> int:
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_auth0 == id_auth0).first()
	if not utilizator:
		utilizator = Utilizator(id_auth0=id_auth0)
		db.add(utilizator)
	else:
		utilizator.data_ultima_conectare = datetime.now(timezone.utc)
	db.commit()
	db.refresh(utilizator)

	return utilizator.id


def get_id_utilizator(id_auth0: str) -> int:
	db = get_session()
	utilizator = db.query(Utilizator).filter(Utilizator.id_auth0 == id_auth0).first()
	return utilizator.id
