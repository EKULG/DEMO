import pandas as pd
import streamlit as st

from mongo_db import create_search_query, pe_backed_with_url
from authentication import is_user_logged_in, logout_user, display_login_page


if 'username' not in st.session_state:
    st.session_state['username'] = None

# LOGIN PAGE
if st.session_state['username'] is None:
    display_login_page()
else:
    # SEARCH PAGE
    if is_user_logged_in(st.session_state['username']):

        data = pe_backed_with_url()

        cols = st.columns(4)

        if 'selected_role' not in st.session_state:
            st.session_state['selected_role'] = ['CFO', 'CEO'][0]

        if 'selected_region' not in st.session_state:
            st.session_state['selected_region'] = data['Region'].unique()[0]

        if 'selected_industry' not in st.session_state:
            st.session_state['selected_industry'] = data['primaryIndustry'].unique()[0]

        selected_role = cols[0].selectbox('Select Role', ['CFO', 'CEO'], index=list(['CFO', 'CEO']).index(st.session_state['selected_role']))

        selected_region = cols[1].selectbox('Select Territory', data['Region'].unique(), index=list(data['Region'].unique()).index(st.session_state['selected_region']))

        selected_industry = cols[2].selectbox('Select Industry', data['primaryIndustry'].unique(), index=list(data['primaryIndustry'].unique()).index(st.session_state['selected_industry']))
        
        cols[3].selectbox('Private Equity', [True])

        if st.button('Search'):
            # Saving Search to Search Query collection
            search_query_id = create_search_query(selected_role, selected_region, selected_industry)
            st.session_state['search_query_id'] = search_query_id
            
            st.session_state['selected_role'] = selected_role
            st.session_state['selected_region'] = selected_region
            st.session_state['selected_industry'] = selected_industry

        if st.button('Logout'):
            logout_user(st.session_state['username'])
            st.session_state['username'] = None
            st.rerun()
    else:
        st.warning("Your session has expired or you've logged out from another tab.")
        st.session_state['username'] = None