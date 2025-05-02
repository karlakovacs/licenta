# import io
# import json
# import tempfile
# from uuid import uuid4

# import matplotlib.pyplot as plt
# import plotly.graph_objects as go
# import plotly.io as pio
# import requests
# import streamlit as st
# from supabase import create_client


# SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
# SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY
# BUCKET_NAME = "test"


# if "supabase_client" not in st.session_state:
# 	st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# supabase = st.session_state.supabase_client


# def conversie_grafic_json(fig: go.Figure) -> dict:
# 	try:
# 		return json.loads(pio.to_json(fig))
# 	except Exception as e:
# 		raise RuntimeError(f"Eroare la conversia graficului: {e}")


# def incarcare_json(json_data: dict) -> str:
# 	file_path = str(uuid4()) + ".json"
# 	try:
# 		json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
# 		supabase.storage.from_(BUCKET_NAME).upload(
# 			file_path, json_bytes, {"content-type": "application/json"}
# 		)
# 		return file_path
# 	except Exception as e:
# 		raise RuntimeError(f"Eroare la încărcarea JSON-ului în Supabase: {e}")


# def incarcare_grafic_json_supabase(fig: go.Figure) -> str:
# 	json_data = conversie_grafic_json(fig)
# 	file_path = incarcare_json(json_data)
# 	return file_path


# def get_json_from_supabase(file_path: str) -> dict:
# 	try:
# 		public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
# 		response = requests.get(public_url)
# 		if response.status_code != 200:
# 			raise RuntimeError(f"Eroare la descărcarea JSON-ului: {response.status_code}")
# 		return response.json()
# 	except Exception as e:
# 		raise RuntimeError(f"Eroare la obținerea fișierului JSON din Supabase: {e}")


# def incarcare_grafic_plt_supabase(fig: plt.Figure, format: str = "svg") -> str:
# 	file_path = str(uuid4()) + "." + format
# 	temp_path = tempfile.gettempdir() + "/" + file_path
# 	fig.savefig(temp_path, format=format, bbox_inches="tight")
# 	content_type = f"image/{format}" if format != "svg" else "image/svg+xml"
# 	supabase.storage.from_(BUCKET_NAME).upload(file_path, temp_path, {"content-type": content_type})
# 	return file_path


# def incarcare_grafic_plt_supabase(fig: plt.Figure, format: str = "svg") -> str:
# 	file_path = str(uuid4()) + ".svg"
# 	buf = io.BytesIO()
# 	fig.savefig(buf, format=format, bbox_inches="tight")
# 	buf.seek(0)
# 	content_type = f"image/{format}" if format != "svg" else "image/svg+xml"
# 	supabase.storage.from_(BUCKET_NAME).upload(
# 		file_path, buf.getvalue(), {"content-type": content_type}
# 	)
# 	return file_path


# def incarcare_grafic_html_supabase(html_data: str) -> str:
# 	file_path = str(uuid4()) + ".html"
# 	buf = io.BytesIO(html_data.encode("utf-8"))
# 	supabase.storage.from_(BUCKET_NAME).upload(
# 		file_path, buf.getvalue(), {"content-type": "text/html"}
# 	)
# 	return file_path


# def get_url_fisier(file_path: str) -> str:
# 	return supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
