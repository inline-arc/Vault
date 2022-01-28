from logging import disable
from pkg_resources import EggMetadata
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from streamlit.state.session_state import SessionState
from streamlit.type_util import Key
import rebel
import wikipedia
from utils import clip_text
from datetime import datetime as dt
import os


wiki_state_variables = {
    'has_run':False,
    'wiki_suggestions': [],
    'wiki_text' : [],
    'nodes':[],
    "topics":[],
}

free_text_state_variables = {
    'has_run':False,
}

def wiki_init_state_variables():
    for k, v in wiki_state_variables.items():
        if k not in st.session_state:
            st.session_state[k] = v

def wiki_generate_graph():
    st.session_state["GRAPH_FILENAME"] = str(dt.now().timestamp()*1000) + ".html"

    if 'wiki_text' not in st.session_state:
        return
    if len(st.session_state['wiki_text']) == 0:
        st.error("please enter a topic and select a wiki page first")
        return
    with st.spinner(text="Generating graph..."):
        texts = st.session_state['wiki_text']
        st.session_state['nodes'] = []
        nodes = rebel.generate_knowledge_graph(texts, st.session_state["GRAPH_FILENAME"])
        print("gen_graph", nodes)
        for n in nodes:
            n = n.lower()
            if n not in st.session_state['topics']:
                st.session_state['nodes'].append(n)
        st.session_state['has_run'] = True
    st.success('Done!')

def wiki_show_suggestion():
    st.session_state['wiki_suggestions'] = []
    with st.spinner(text="fetching wiki topics..."):
        if st.session_state['input_method'] == "wikipedia":
            text = st.session_state.text
            if text is not None:
                subjects = text.split(",")
                for subj in subjects:
                    st.session_state['wiki_suggestions'] += wikipedia.search(subj, results = 3)

def wiki_show_text(page_title):
    with st.spinner(text="fetching wiki page..."):
        try:
            page = wikipedia.page(title=page_title, auto_suggest=False)
            st.session_state['wiki_text'].append(clip_text(page.summary))
            st.session_state['topics'].append(page_title.lower())
        except wikipedia.DisambiguationError as e:
            with st.spinner(text="Woops, ambigious term, recalculating options..."):
                st.session_state['wiki_suggestions'].remove(page_title)
                temp = st.session_state['wiki_suggestions'] + e.options[:3]
                st.session_state['wiki_suggestions'] = list(set(temp))

def wiki_add_text(term):
    if len(st.session_state['topics']) > 4:
        return
    try:
        extra_text = clip_text(wikipedia.page(title=term, auto_suggest=False).summary)
        st.session_state['wiki_text'].append(extra_text)
        st.session_state['topics'].append(term.lower())
    except wikipedia.DisambiguationError as e:
        with st.spinner(text="Woops, ambigious term, recalculating options..."):
            st.session_state['nodes'].remove(term)
            temp = st.session_state['nodes'] + e.options[:3]
            st.session_state['node'] = list(set(temp))
    except wikipedia.WikipediaException:
        st.session_state['nodes'].remove(term)

def wiki_reset_session():
    for k in wiki_state_variables:
        del st.session_state[k]

def free_text_generate():
    st.session_state["GRAPH_FILENAME"] = str(dt.now().timestamp()*1000) + ".html"

    text = st.session_state['free_text'][0:500]
    rebel.generate_knowledge_graph([text], st.session_state["GRAPH_FILENAME"])
    st.session_state['has_run'] = True

def free_text_layout():
    st.text_input("Free text", key="free_text")
    st.button("Generate", on_click=free_text_generate, key="free_text_generate")


st.title('REBELious knowledge graph generation')
st.selectbox(
     'input method',
     ('wikipedia', 'free text'),  key="input_method")


def show_wiki_hub_page():
    st.sidebar.markdown(
"""
# how to
- Enter wikipedia search terms, separated by comma's
- Choose one or more of the suggested pages
- Click generate!
"""
)
    st.sidebar.button("Reset", on_click=wiki_reset_session, key="reset_key")
    cols = st.columns([8, 1])
    with cols[0]:
        st.text_input("wikipedia search term", on_change=wiki_show_suggestion, key="text")
    with cols[1]:
        st.text('')
        st.text('')
        st.button("Search", on_click=wiki_show_suggestion, key="show_suggestion_key")

    if len(st.session_state['wiki_suggestions']) != 0:
        num_buttons = len(st.session_state['wiki_suggestions'])
        num_cols = num_buttons if 0 < num_buttons < 8 else 8
        columns = st.columns([1] * num_cols )
        for q in range(1 + num_buttons//num_cols):
            for i, (c, s) in enumerate(zip(columns, st.session_state['wiki_suggestions'][q*num_cols: (q+1)*num_cols])):
                with c:
                    st.button(s, on_click=wiki_show_text, args=(s,), key=str(i)+s)

    if len(st.session_state['wiki_text']) != 0:
        for i, t in enumerate(st.session_state['wiki_text']):
            new_expander = st.expander(label=t[:30] + "...", expanded=(i==0))
            with new_expander:
                st.markdown(t)

    if len(st.session_state['wiki_text']) > 0:
        st.button("Generate", on_click=wiki_generate_graph, key="gen_graph")
    st.sidebar.markdown(
        """
    # How to expand the graph
    - Click a button on the right to expand that node
    - Only nodes that have wiki pages will be expanded
    - Hit the Generate button again to expand your graph!
    """
    )
    if st.session_state['has_run']:


        HtmlFile = open(st.session_state["GRAPH_FILENAME"], 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, width=720, height=600)
        os.remove(st.session_state["GRAPH_FILENAME"])
        num_buttons = len(st.session_state["nodes"])
        num_cols = num_buttons if 0 < num_buttons < 7 else 7
        columns = st.columns([1] * num_cols + [1])
        print(st.session_state["nodes"])

        for q in range(1 + num_buttons//num_cols):
            for i, (c, s) in enumerate(zip(columns, st.session_state["nodes"][q*num_cols: (q+1)*num_cols])):
                with c:
                    st.button(s, on_click=wiki_add_text, args=(s,), key=str(i)+s)

def show_free_text_hub_page():
    st.sidebar.markdown(
"""
# How to
- Enter a text you'd like to see as a graph.
- Click generate!
"""
)
    st.sidebar.markdown(
    """
# How to expand the graph
- Click a button on the right to expand that node
- Only nodes that have wiki pages will be expanded
- Hit the Generate button again to expand your graph!
"""
)

    st.sidebar.button("Reset", key="reset_key")
    free_text_layout()
    if st.session_state['has_run']:
        HtmlFile = open(st.session_state["GRAPH_FILENAME"], 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, width=720, height=600)
        os.remove(st.session_state["GRAPH_FILENAME"])

if st.session_state['input_method'] == "wikipedia":
    wiki_init_state_variables()
    show_wiki_hub_page()
else:
    show_free_text_hub_page()


st.sidebar.markdown(
"""
*Credits for the REBEL model go out to Pere-Lluís Huguet Cabot and Roberto Navigli.
The code can be found [here](https://github.com/Babelscape/rebel),
and the original paper [here](https://github.com/Babelscape/rebel/blob/main/docs/EMNLP_2021_REBEL__Camera_Ready_.pdf)*
"""
)