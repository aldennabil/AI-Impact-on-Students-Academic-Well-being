import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis AI Mahasiswa",
    layout="wide",
    initial_sidebar_state="expanded",
)

overview_page    = st.Page("pages/1_Overview.py",    title="Ringkasan Umum",  default=True)
segmentasi_page  = st.Page("pages/2_Segmentasi.py",  title="Segmentasi")

pg = st.navigation([overview_page, segmentasi_page])
pg.run()
