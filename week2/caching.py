import streamlit as st
import time

@st.cache_data
def my_slow_function(arg1, arg2):
    time.sleep(3)
    return arg1 + arg2

result = my_slow_function(10, 20)
st.write(result)