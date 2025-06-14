from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from storage import *

from ..modele import Metrici, Model, ModeleMetrici, TipModel
from ..utils import get_session


def create_model(
	id_set_date_procesat: int, id_tip_model: int, hiperparametri: dict, durata_antrenare: float, url: str
) -> int:
	db = get_session()

	model = Model(
		id_set_date_procesat=id_set_date_procesat,
		id_tip_model=id_tip_model,
		hiperparametri=hiperparametri,
		durata_antrenare=durata_antrenare,
		url=url,
		data_antrenare=datetime.now(timezone.utc),
	)

	db.add(model)
	db.commit()
	db.refresh(model)

	return model.id


def create_modele(id_utilizator: int, id_set_date_procesat: int, modele_antrenate: dict) -> dict[str, int]:
	db = get_session()

	tipuri = db.query(TipModel).all()
	denumire_to_id = {t.denumire: t.id for t in tipuri}

	modele_de_salvat = []
	now = datetime.now(timezone.utc)
	dict_rezultat = {}

	for denumire_model, valori in modele_antrenate.items():
		id_tip_model = denumire_to_id.get(denumire_model)
		if id_tip_model is None:
			print(f"Modelul '{denumire_model}' nu există în TipModel.")
			continue

		url = upload_model_to_storage(valori.get("model"), id_utilizator, id_set_date_procesat, denumire_model)

		model_obj = Model(
			id_set_date_procesat=id_set_date_procesat,
			id_tip_model=id_tip_model,
			hiperparametri=valori.get("hiperparametri", {}),
			durata_antrenare=valori.get("timp", 0.0),
			url=url,
			data_antrenare=now,
		)

		modele_de_salvat.append(model_obj)
		dict_rezultat[denumire_model] = model_obj

	db.add_all(modele_de_salvat)
	db.commit()
	db.flush()

	return {nume: obj.id for nume, obj in dict_rezultat.items()}


# ids modele-> dict cu nume modele si ids
# metrici -> dict cu nume modele si un alt dict imbricat de metrici
# def create_metrici(ids_modele: dict, metrici: dict) -> None:
# 	db = get_session()

# 	toate_metricile = db.query(Metrici).all()
# 	prescurtare_to_id = {m.prescurtare: m.id for m in toate_metricile}

# 	metrici_de_salvat = []

# 	for prescurtare, valoare in metrici.items():
# 		id_metrica = prescurtare_to_id.get(prescurtare)
# 		if id_metrica is None:
# 			print(f"Metrica '{prescurtare}' nu există în tabela 'metrici'.")
# 			continue

# 		metrica_model = ModeleMetrici(id_model=id_model, id_metrica=id_metrica, valoare=valoare)
# 		metrici_de_salvat.append(metrica_model)

# 	db.add_all(metrici_de_salvat)
# 	db.commit()


def create_metrici(ids_modele: dict[str, int], metrici: dict[str, dict[str, float]]) -> None:
	db = get_session()

	tipuri_metrici = db.query(Metrici).all()
	prescurtare_to_id = {m.prescurtare: m.id for m in tipuri_metrici}

	metrici_de_salvat = []

	for nume_model, id_model in ids_modele.items():
		metrici_model = metrici.get(nume_model, {})

		for prescurtare, valoare in metrici_model.items():
			id_metrica = prescurtare_to_id.get(prescurtare)

			if id_metrica is None:
				print(f"Metrica '{prescurtare}' nu există în tabela 'metrici'.")
				continue

			metrica_model = ModeleMetrici(
				id_model=id_model,
				id_metrica=id_metrica,
				valoare=valoare,
			)
			metrici_de_salvat.append(metrica_model)

	db.add_all(metrici_de_salvat)
	db.commit()


def get_modele(id_set_date_procesat: int) -> list:
	db = get_session()

	modele = (
		db.query(Model)
		.options(joinedload(Model.tip_model), joinedload(Model.metrici).joinedload(ModeleMetrici.metrica))
		.filter(Model.id_set_date_procesat == id_set_date_procesat)
		.all()
	)

	lista = []
	for model in modele:
		inregistrare = {
			"Tip model": model.tip_model.denumire if model.tip_model else None,
			"URL": f"[⬇️ Descarcă modelul]({SUPABASE_URL}/storage/v1/object/public/models/{model.url}?download={os.path.basename(model.url)})",
			"Durată antrenare": model.durata_antrenare,
			"Dată antrenare": model.data_antrenare,
			"Hiperparametri": model.hiperparametri,
		}

		for metrica in model.metrici:
			inregistrare[metrica.metrica.denumire] = metrica.valoare

		lista.append(inregistrare)

	return lista


def delete_model(id_model: int) -> tuple[bool, str]:
	db = get_session()

	model = db.query(Model).filter_by(id=id_model).first()
	if not model:
		return False, "Modelul nu există"

	db.query(ModeleMetrici).filter_by(id_model=id_model).delete()

	db.delete(model)
	db.commit()

	return True, "Modelul a fost șters"
