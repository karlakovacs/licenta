from functools import wraps

import streamlit as st

from .utils import verificare_flag


def require_auth(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not getattr(st.user, "sub", None):
			st.warning("🔐 Nu ești autentificat. Te rugăm să accesezi pagina de start pentru autentificare.")
			st.switch_page("app.py")
			st.stop()
		return func(*args, **kwargs)

	return wrapper


def require_selected_dataset(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not verificare_flag("selected_dataset"):
			st.warning("📁 Nu ai selectat un set de date.")
			st.stop()
		return func(*args, **kwargs)

	return wrapper


def require_processed_dataset(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not verificare_flag("processed_dataset"):
			st.warning("🏭 Setul de date nu a fost procesat.")
			st.stop()
		return func(*args, **kwargs)

	return wrapper


def require_selected_models(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not verificare_flag("selected_models"):
			st.warning("🤖 Nu ai selectat modele ML pentru antrenare.")
			st.stop()
		return func(*args, **kwargs)

	return wrapper


def require_trained_models(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not verificare_flag("trained_models"):
			st.warning("🚀 Modelele ML nu sunt antrenate.")
			st.stop()
		return func(*args, **kwargs)

	return wrapper
