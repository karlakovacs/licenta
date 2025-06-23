import mimetypes
import os
import pickle
import tempfile
import uuid

import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def serialize_model(model, denumire_model: str, format_hint: str = None) -> str:
	try:
		import sklearn.base

		if isinstance(model, sklearn.base.BaseEstimator) or format_hint == "pickle":
			temp_path = os.path.join(tempfile.gettempdir(), f"{denumire_model}.pkl")
			with open(temp_path, "wb") as f:
				pickle.dump(model, f)
			return temp_path

		import xgboost as xgb

		if isinstance(model, xgb.XGBModel) or format_hint == "xgboost":
			temp_path = os.path.join(tempfile.gettempdir(), f"{denumire_model}.json")
			model.save_model(temp_path)
			return temp_path

		import lightgbm as lgb

		if isinstance(model, lgb.LGBMModel) or format_hint == "lightgbm":
			temp_path = os.path.join(tempfile.gettempdir(), f"{denumire_model}.txt")
			model_str = model.booster_.model_to_string()
			with open(temp_path, "w", encoding="utf-8") as f:
				f.write(model_str)
			return temp_path

		import catboost

		if isinstance(model, catboost.CatBoost) or format_hint == "catboost":
			temp_path = os.path.join(tempfile.gettempdir(), f"{denumire_model}.cbm")
			model.save_model(temp_path)
			return temp_path

		from keras.api.models import Sequential

		if isinstance(model, Sequential) or format_hint == "keras":
			temp_path = os.path.join(tempfile.gettempdir(), f"{denumire_model}.keras")
			model.save(temp_path)
			return temp_path

		raise ValueError("Tip de model nesuportat automat. Specifică manual `format_hint`.")

	except Exception as e:
		raise RuntimeError(f"Eroare la serializarea modelului: {e}")


def upload_model_to_storage(
	model, id_utilizator: int, id_set_date_procesat: int, tip_model: str, bucket: str = "models"
) -> str:
	temp_path: str = serialize_model(model, tip_model)

	_, ext = os.path.splitext(temp_path)

	cale = f"{id_utilizator}/{id_set_date_procesat}/{tip_model}_{uuid.uuid4().hex}{ext}"

	mime_type, _ = mimetypes.guess_type(temp_path)
	if not mime_type:
		mime_type = "application/octet-stream"

	with open(temp_path, "rb") as f:
		supabase.storage.from_(bucket).upload(cale, f, {"content-type": mime_type})

	os.remove(temp_path)

	return cale


def get_model_url_from_storage(model, bucket: str = "models") -> str:
	path = model.url
	filename = os.path.basename(path)
	return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}?download={filename}"
