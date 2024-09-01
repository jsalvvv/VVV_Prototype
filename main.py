import streamlit as st
from tools.api import get_request
from tools.utils import render_search_results, render_detailed_search

st.title("Virtual Vocation Ventures Career Helper")

search_container = st.container()
with search_container:
    with st.form("search_form"):
        search_input = st.text_input("Search for an Occupation")
        result_size = st.slider("Result Size", 1, 100, 10)
        call_search = st.form_submit_button("Search")
    
# Search for an occupation given keyword
if call_search:
    results = get_request(
        "https://services.onetcenter.org/ws/online/search", 
        {
            "keyword": search_input,
            "start": 1,
            "end": result_size
        }
    )
    render_search_results(results, st.form('detailed_search_form'))

if st.session_state.get("detailed_search_form"):
    request_data = st.session_state.get("detailed_search_form")
    
    # Render the detailed search form
    render_detailed_search(request_data, st.container())
