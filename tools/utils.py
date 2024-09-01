import streamlit as st
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
from tools.api import get_request
from requests.exceptions import HTTPError


def render_search_results(data: dict, parent_container: DeltaGenerator) -> None:
    # Parse JSON response into a pandas DataFrame
    df = pd.json_normalize(data, 'occupation')
    
    # Exclude specific columns from table
    df = df.drop(columns=[
        'relevance_score',
        'tags.bright_outlook',
        'tags.green'
    ])
    
    # Render Table
    parent_container.subheader('Search Results')
    parent_container.write(f"Keyword: {data.get('keyword')}")
    parent_container.write(f"Showing Results: {data.get('start')} - {data.get('end')}")
    
    # Render link buttons in table-like structure
    for _, row in df.iterrows():
        title = row.get('title')
        code = row.get('code')
        parent_container.form_submit_button(title, on_click=lambda title=title, code=code: st.session_state.update({"detailed_search_form": {"title": title, "code": code}}))


def render_top_technology_skills(
    code: str, 
    pc: DeltaGenerator, 
    n: int = 5
) -> None:
    # Request Top Technology Skills given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/summary/technology_skills"
    params = {
        "display": "long"
    }
    result = get_request(url, params)
    
    categories = result.get('category', [])
    
    pc.subheader(f"Top {n} Technology Skills")
    for category in categories[:n]:
        name = category.get('title').get('name')
        with st.expander(label=("💡" + name)):
            examples = category.get('example')
            st.caption("Hot Technologies are requirements frequently included in employer job postings.")
            for example in examples:
                st.write(f":fire: {example.get('name')}")

def render_top_skills(
    code: str, 
    pc: DeltaGenerator, 
    n: int = 5
) -> None:
    # Request Top Technology Skills given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/skills"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Skills data is not available in the Details report for this occupation.")
        return
    
    elements = result.get('element', [])
    
    pc.subheader(f"Top {n} Skills")
    for skill in elements[:n]:
        name = skill.get('name')
        with st.expander(label=("💡" + name)):
            st.caption(f"{skill.get('description')}")
            score = skill.get('score')
            st.progress((score.get('value') / 100), (str(score.get('value')) + "%"))

def render_overview(
    code: str, 
    pc: DeltaGenerator
):
        # Request Top Technology Skills given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/"
    result = get_request(url)
    
    # Description
    pc.caption("Description")
    pc.write(f"{result.get('description')}")
    
    # Bright Outlook
    bright_outlook = result.get('bright_outlook', None)
    if bright_outlook is not None:
        pc.success(f":sun_with_face: Bright Job Outlook")
        pc.caption(f"{bright_outlook.get('description', '')}")
    
    # Green
    green = result.get('green', None)
    if green is not None:
        pc.caption("Green :herb:")
        pc.write(f"{green.get('category', '')}: {green.get('description', '')}")

def render_education(
    code: str, 
    pc: DeltaGenerator, 
) -> None:
    # Request Education given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/education"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Education data is not available in the Details report for this occupation.")
        return
    
    pc.subheader("Education")
    pc.caption(f"Typical Education Levels")
    categories = result.get('level_required', {}).get('category', [])
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        with cols[i]:
            st.write(category.get('name'))
            score = category.get('score', {})
            st.metric(label=f"{score.get('value', '')}", value=f"{score.get('value')}%", label_visibility="collapsed")
            st.caption(f"{score.get('scale', '')}")

def render_work_activities(
    code: str, 
    pc: DeltaGenerator,
    n = 5
):
    # Request Work Activities given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/work_activities"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Work Activities data is not available in the Details report for this occupation.")
        return
    
    pc.subheader(f"Top {n} Work Activities")
    
    elements = result.get('element', [])
    for elem in elements[:n]:
        name = elem.get('name')
        with st.expander(label=("💡" + name)):
            st.caption(f"{elem.get('description')}")
            score = elem.get('score')
            st.progress((score.get('value') / 100), (str(score.get('value')) + "%"))

def render_work_context_details(
    code: str, 
    pc: DeltaGenerator,
    n = 5
):
    # Request Work Context Details given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/work_context"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Work Context Details data is not available in the Details report for this occupation.")
        return
    
    pc.subheader(f"Top {n} Work Context Details")
    
    elements = result.get('element', [])
    for elem in elements[:n]:
        description = elem.get('description')
        with st.expander(label=("💡" + description)):
            response = elem.get('response', [])
            for r in response:
                st.subheader(str(r.get('percentage')) + "%")
                st.progress(value = (r.get('percentage') / 100), text = r.get('name', ''))

def render_job_zone_details(
    code: str, 
    pc: DeltaGenerator
):
    # Request Job Zone Details given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/job_zone"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Job Zone Details data is not available in the Details report for this occupation.")
        return

    # Remove "Job Zone " prefix from title
    title = result.get('title').replace("Job Zone ", "")
    score = result.get('value', 1)
    # Based on score render different elements
    score_widget_map = {
        1: pc.success,
        2: pc.info,
        3: pc.warning,
        4: pc.warning
    }
    widget = score_widget_map.get(score)
    widget(f"Job Zone {title}")
    # Subheaders
    values = ["education", "related_experience", "job_training", "job_zone_examples"]
    for v in values:
        pc.subheader(v.replace("_", " ").title())
        pc.caption(result.get(v))

def render_work_values(
    code: str, 
    pc: DeltaGenerator,
    n = 5
):
    # Request Work Values given a code and render elements to parent
    url = f"https://services.onetcenter.org/ws/online/occupations/{code}/details/work_values"
    params = {}
    try:
        result = get_request(url, params)
    except HTTPError as e:
        pc.warning("Work Values data is not available in the Details report for this occupation.")
        return
    
    pc.subheader(f"Top {n} Work Values")
    
    elements = result.get('element', [])
    for elem in elements[:n]:
        name = elem.get('name')
        with st.expander(label=("💡" + name)):
            st.caption(f"{elem.get('description')}")
            score = elem.get('score')
            st.progress((score.get('value') / 100), (str(score.get('value')) + "%"))

def render_detailed_search(request_data: dict, parent_container: DeltaGenerator) -> None:
    # Parent function to call single responsibility functions
    parent_container.header(request_data.get('title'))
    
    # Render Overview
    render_overview(request_data.get('code'), parent_container)
    render_job_zone_details(request_data.get('code'), parent_container)
    
    st.divider()
    # Group Skills in Columns
    col1, col2 = st.columns(2)
    with col1:
        # Render Top Technology Skills
        render_top_technology_skills(request_data.get('code'), st.container())
    with col2:
        # Render Top Skills
        render_top_skills(request_data.get('code'), st.container())
    
    # Education
    render_education(request_data.get('code'), st.container())
    
    # Is it right for me?
    job_fit_container = st.container()
    job_fit_container.header("Is this right for me?")
    
    render_work_activities(request_data.get('code'), st.container())
    render_work_context_details(request_data.get('code'), st.container())
    render_work_values(request_data.get('code'), st.container())