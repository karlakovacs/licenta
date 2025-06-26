from auth0.authentication import GetToken
from auth0.management import Auth0
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


def get_auth0():
	DOMAIN = st.secrets.auth0.DOMAIN
	CLIENT_ID = st.secrets.auth0.CLIENT_ID
	CLIENT_SECRET = st.secrets.auth0.CLIENT_SECRET

	get_token = GetToken(DOMAIN, CLIENT_ID, CLIENT_SECRET)
	token = get_token.client_credentials("https://{}/api/v2/".format(DOMAIN))
	mgmt_api_token = token["access_token"]
	auth0 = Auth0(DOMAIN, mgmt_api_token)

	return auth0
