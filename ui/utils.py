import streamlit as st

from database import get_id_utilizator

from .nav_bar import nav_bar


def setare_id_utilizator():
	if "id_utilizator" not in st.session_state:
		user_sub = getattr(st.user, "sub", None)
		st.session_state.setdefault("id_utilizator", get_id_utilizator(user_sub))


def initializare_cheie(cheie: str, valoare):
	st.session_state.setdefault(cheie, valoare)


def setare_cheie(cheie: str, valoare):
	st.session_state[cheie] = valoare


def initializare_cheie_imbricata(cheie_dictionar: str, cheie: str, valoare):
	if cheie_dictionar not in st.session_state:
		st.session_state[cheie_dictionar] = {}

	if cheie not in st.session_state[cheie_dictionar]:
		st.session_state[cheie_dictionar][cheie] = valoare


def setare_cheie_imbricata(cheie_dictionar: str, cheie: str, valoare):
	if cheie_dictionar not in st.session_state:
		st.session_state[cheie_dictionar] = {}

	st.session_state[cheie_dictionar][cheie] = valoare


def obtinere_cheie(cheie: str, default=None):
	return st.session_state.get(cheie, default)


def obtinere_cheie_imbricata(cheie_dictionar: str, cheie: str, default=None):
	return st.session_state.get(cheie_dictionar, {}).get(cheie, default)


def configurare(dictionar_configurare: dict):
	for cheie, valoare in dictionar_configurare.items():
		initializare_cheie(cheie, valoare)


def verificare_utilizator_logat():
	if not getattr(st.user, "sub", None):
		st.warning("Nu ești autentificat.")
		st.stop()


def configurare_pagina(titlu_pagina: str, layout: str = "wide"):
	st.set_page_config(layout=layout, page_title=f"{titlu_pagina} | FlagML", page_icon="assets/logo.png")


def setare_titlu_pagina(titlu_interfata: str):
	st.title(titlu_interfata)


def initializare_pagina(titlu_pagina: str, layout: str, titlu_interfata: str, dictionar_configurare: dict = None):
	configurare_pagina(titlu_pagina, layout)
	nav_bar()
	verificare_utilizator_logat()
	setare_id_utilizator()
	initializare_flaguri()
	if dictionar_configurare is not None:
		configurare(dictionar_configurare)
	setare_titlu_pagina(titlu_interfata)


def initializare_flaguri():
	if "flags" not in st.session_state:
		flaguri = ["selected_dataset", "processed_dataset", "selected_models", "trained_models"]
		for flag in flaguri:
			initializare_cheie_imbricata("flags", flag, False)


def setare_flag(flag: str):
	setare_cheie_imbricata("flags", flag, True)


def verificare_flag(flag: str):
	return obtinere_cheie_imbricata("flags", flag, False)
