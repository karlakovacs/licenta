import pandas as pd
import streamlit as st

from ui import *


initializare_pagina("Documentație", "wide", "Documentație")


@require_auth
def main():
	st.write("Aici puteți citi documentația aplicației.")


if __name__ == "__main__":
	main()
