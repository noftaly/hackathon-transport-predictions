import streamlit as st
from utils import *
import time

before_load = time.time()
load_data_validations()
load_data_velib()

if time.time() - before_load > 2:
    st.balloons()

st.title('Transport statistics in Île-De-France')

# st.set_page_config(layout="wide")
