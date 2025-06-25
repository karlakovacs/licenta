from datetime import datetime

import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_report_to_storage(id_utilizator: int, html_bytes: bytes, bucket: str = "reports") -> dict:
	date = datetime.now()
	date_str = date.strftime("%Y-%m-%d-%H-%M-%S")
	path = f"{id_utilizator}/raport_{date_str}.html"
	supabase.storage.from_(bucket).upload(path, html_bytes, {"content-type": "text/html"})
	return path, date


def get_report_url_from_storage(raport, bucket: str = "reports"):
	url = raport.url
	denumire_fisier = f"raport_{url.split('/')[-1]}"
	html_url = (
		f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{url}?download={denumire_fisier}.html"
	)
	return html_url


def delete_report_from_storage(raport, bucket: str = "reports"):
	try:
		url = raport.url
		supabase.storage.from_(bucket).remove(url)
		return True, "Raportul a fost șters."
	except:
		return False, "A avut loc o eroare la ștergerea raportului."
