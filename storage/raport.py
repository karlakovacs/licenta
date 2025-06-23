from datetime import datetime, timezone

import streamlit as st
from supabase import create_client


SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_reports_to_storage(id_utilizator: int, html_bytes: bytes, pdf_bytes: bytes, bucket: str = "reports") -> dict:
	data = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
	base_path = f"{id_utilizator}/{data}"
	html_path = f"{base_path}/raport_{data}.html"
	pdf_path = f"{base_path}/raport_{data}.pdf"
	supabase.storage.from_(bucket).upload(html_path, html_bytes, {"content-type": "text/html"})
	supabase.storage.from_(bucket).upload(pdf_path, pdf_bytes, {"content-type": "application/pdf"})

	return base_path


def get_report_urls_from_storage(raport, bucket: str = "reports"):
	url = raport.url
	denumire_fisier = f"raport_{url.split('/')[-1]}"
	html_url = (
		f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{url}/{denumire_fisier}.html?download={denumire_fisier}.html"
	)
	pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{url}/{denumire_fisier}.pdf"
	return html_url, pdf_url


def delete_reports_from_storage(raport, bucket: str = "reports"):
	url = raport.url
	prefix_folder = url + "/"
	try:
		files = supabase.storage.from_(bucket).list(prefix_folder)
		for file in files:
			supabase.storage.from_(bucket).remove(f"{prefix_folder}{file['name']}")
		return True, "Raportul a fost șters."
	except:
		return False, "A avut loc o eroare la ștergerea raportului."
