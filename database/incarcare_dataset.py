import _io
import tempfile
from uuid import uuid4

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import streamlit as st
from supabase import Client, create_client


MAX_UPLOAD_SIZE = 50
CHUNK_SIZE = 45

SUPABASE_URL = st.secrets.supabase.SUPABASE_URL
SUPABASE_KEY = st.secrets.supabase.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def incarcare_datasets(parquet_files, bucket_name="datasets"):
	try:
		for file_path in parquet_files:
			file_name = os.path.basename(file_path)

			with open(file_path, "rb") as f:
				supabase.storage.from_(bucket_name).upload(file_name, f)

			st.write(f"✅ Încărcat: {file_name}")

	except Exception as e:
		st.error(f"Eroare la încărcare: {e}")
		return e


def salvare_split_parquet(fisier_incarcat: _io.BytesIO):
	df = pd.read_csv(fisier_incarcat)
	table = pa.Table.from_pandas(df)
	total_size = table.nbytes / (1024 * 1024)

	parquet_files = []

	with tempfile.TemporaryDirectory() as temp_dir:
		if total_size < MAX_UPLOAD_SIZE:
			file_path = os.path.join(temp_dir, "data.parquet")
			pq.write_table(table, file_path)
			parquet_files.append(file_path)
		else:
			num_splits = max(1, int(total_size / CHUNK_SIZE))
			row_splits = len(df) // num_splits

			for i in range(num_splits):
				start_row = i * row_splits
				end_row = (i + 1) * row_splits if i != num_splits - 1 else len(df)
				df_chunk = df.iloc[start_row:end_row]

				file_path = os.path.join(temp_dir, f"{i}.parquet")
				pq.write_table(pa.Table.from_pandas(df_chunk), file_path)
				parquet_files.append(file_path)

		return parquet_files
