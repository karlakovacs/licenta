from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st


# DATABASE_URL = st.secrets.supabase.DATABASE_URL
DATABASE_URL = st.secrets.local.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
