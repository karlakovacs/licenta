from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import streamlit as st


@st.cache_resource
def get_engine():
	DATABASE_URL = st.secrets.supabase.DATABASE_URL
	return create_engine(DATABASE_URL)


def get_session():
	engine = get_engine()
	Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
	return Session()
