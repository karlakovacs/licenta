from datetime import datetime, timezone
import io
import os
import shutil
import tempfile
import uuid

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import streamlit as st
from supabase import create_client


CHUNK_SIZE = 50
SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def scriere_chunk(df_chunk, path) -> float:
	table = pa.Table.from_pandas(df_chunk)
	pq.write_table(table, path)
	size_bytes = os.path.getsize(path)
	return size_bytes / (1024 * 1024)


def incarcare_dataset_supabase(
	df: pd.DataFrame, id_utilizator: int, denumire_dataset: str, bucket: str = "datasets"
) -> str:
	temp_dir = tempfile.mkdtemp()
	folder_uuid = uuid.uuid4()
	folder = f"{id_utilizator}/{denumire_dataset}_{folder_uuid}"

	try:
		approx_row_size = df.memory_usage(deep=True).sum() / len(df)
		rows_per_chunk = int((CHUNK_SIZE * 1024 * 1024) / approx_row_size)

		part_idx = 0
		for start in range(0, len(df), rows_per_chunk):
			chunk = df.iloc[start : start + rows_per_chunk]
			file_name = f"{part_idx}.parquet"
			file_path = os.path.join(temp_dir, file_name)

			size_mb = scriere_chunk(chunk, file_path)

			if size_mb > CHUNK_SIZE and len(chunk) > 1:
				half = len(chunk) // 2
				for sub_chunk in [chunk.iloc[:half], chunk.iloc[half:]]:
					sub_file_name = f"{part_idx}.parquet"
					sub_file_path = os.path.join(temp_dir, sub_file_name)
					scriere_chunk(sub_chunk, sub_file_path)

					with open(sub_file_path, "rb") as f:
						supa_path = f"{folder}/{sub_file_name}"
						supabase.storage.from_(bucket).upload(supa_path, f)
					part_idx += 1
			else:
				with open(file_path, "rb") as f:
					supa_path = f"{folder}/{file_name}"
					supabase.storage.from_(bucket).upload(supa_path, f)
				part_idx += 1

		return folder

	finally:
		shutil.rmtree(temp_dir)


def citire_dataset_supabase(folder: str, bucket: str = "datasets") -> pd.DataFrame:
	storage = supabase.storage.from_(bucket)
	files = storage.list(folder)
	parquet_files = [f["name"] for f in files if f["name"].endswith(".parquet")]
	sorted_files = sorted(parquet_files, key=lambda name: int(name.replace(".parquet", "")))

	dfs = []
	for file_name in sorted_files:
		file_path = f"{folder}/{file_name}"

		content = storage.download(file_path)
		df = pd.read_parquet(io.BytesIO(content))
		dfs.append(df)

	df = pd.concat(dfs, ignore_index=True)
	return df


def citire_sample_dataset_supabase(folder: str, bucket: str = "datasets") -> pd.DataFrame:
	storage = supabase.storage.from_(bucket)
	file_path = f"{folder}/0.parquet"

	content = storage.download(file_path)
	df = pd.read_parquet(io.BytesIO(content))
	return df.head()


def incarcare_rapoarte_supabase(
	id_utilizator: int, html_bytes: bytes, pdf_bytes: bytes, bucket: str = "reports"
) -> dict:
	data = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
	base_path = f"{id_utilizator}/{data}"
	html_path = f"{base_path}/raport_{data}.html"
	pdf_path = f"{base_path}/raport_{data}.pdf"
	supabase.storage.from_(bucket).upload(html_path, html_bytes, {"content-type": "text/html"})
	supabase.storage.from_(bucket).upload(pdf_path, pdf_bytes, {"content-type": "application/pdf"})

	return base_path


# df = pd.read_parquet("C:/Users/karla/Desktop/licenta_app/data/mlg-ulb.parquet")
# cale_folder = incarcare_dataset_supabase(df, 1, denumire_dataset="mlg_ulb")
# df_citit = citire_dataset_supabase(cale_folder)
# print(df_citit.head())
