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

network_filename = "test.html"

state_variables = {
    'has_run':False,
    'wiki_suggestions': [],
    'wiki_text' : [],
    'nodes':[]
}

for k, v in state_variables.items():
    if k not in st.session_state:
        st.session_state[k] = v

def clip_text(t, lenght = 10):
    return ".".join(t.split(".")[:lenght]) + "."


def generate_graph():
    if 'wiki_text' not in st.session_state:
        return
    if len(st.session_state['wiki_text']) == 0:
        st.error("please enter a topic and select a wiki page first")
        return
    with st.spinner(text="Generating graph..."):
        texts = st.session_state['wiki_text']
        nodes = rebel.generate_knowledge_graph(texts, network_filename)
        st.session_state['nodes'] = nodes
        st.session_state['has_run'] = True
    st.success('Done!')

def show_suggestion():
    st.session_state['wiki_suggestions'] = []
    with st.spinner(text="fetching wiki topics..."):
        if st.session_state['input_method'] == "wikipedia":
            text = st.session_state.text
            if text is not None:
                subjects = text.split(",")
                for subj in subjects:
                    st.session_state['wiki_suggestions'] += wikipedia.search(subj, results = 3)

def show_wiki_text(page_title):
    with st.spinner(text="fetching wiki page..."):
        try:
            page = wikipedia.page(title=page_title, auto_suggest=False)
            st.session_state['wiki_text'].append(clip_text(page.summary))
        except wikipedia.DisambiguationError as e:
            with st.spinner(text="Woops, ambigious term, recalculating options..."):
                st.session_state['wiki_suggestions'].remove(page_title)
                temp = st.session_state['wiki_suggestions'] + e.options[:3]
                st.session_state['wiki_suggestions'] = list(set(temp))

def add_text(term):
    try:
        extra_text = clip_text(wikipedia.page(title=term, auto_suggest=True).summary)
        st.session_state['wiki_text'].append(extra_text)
    except wikipedia.WikipediaException:
        st.error("Woops, no wikipedia page for this node")
        st.session_state["nodes"].remove(term)

def reset_session():
    for k in state_variables:
        del st.session_state[k]

st.title('REBELious knowledge graph generation')
st.session_state['input_method'] = "wikipedia"

st.sidebar.markdown(
"""
# how to
- Enter wikipedia search terms, separated by comma's
- Choose one or more of the suggested pages
- Click generate!
"""
)

st.sidebar.button("Reset", on_click=reset_session, key="reset_key")

# st.selectbox(
#      'input method',
#      ('wikipedia', 'free text'),  key="input_method")

if st.session_state['input_method'] != "wikipedia":
    # st.text_area("Your text", key="text")
    pass
else:
    cols = st.columns([8, 1])
    with cols[0]:
        st.text_input("wikipedia search term", on_change=show_suggestion, key="text")
    with cols[1]:
        st.text('')
        st.text('')
        st.button("Search", on_click=show_suggestion, key="show_suggestion_key")

if len(st.session_state['wiki_suggestions']) != 0:

    num_buttons = len(st.session_state['wiki_suggestions'])
    num_cols = num_buttons if num_buttoms < 7 else 7
    columns = st.columns([1] * num_cols + [1])
    print(st.session_state['wiki_suggestions'])

    for q in range(1 + num_buttons//num_cols):
        for i, (c, s) in enumerate(zip(columns, st.session_state['wiki_suggestions'][q*num_cols: (q+1)*num_cols])):
            with c:
                st.button(s, on_click=show_wiki_text, args=(s,), key=str(i)+s)

if len(st.session_state['wiki_text']) != 0:
    for i, t in enumerate(st.session_state['wiki_text']):
        new_expander = st.expander(label=t[:30] + "...", expanded=(i==0))
        with new_expander:
            st.markdown(t)

if st.session_state['input_method'] != "wikipedia":
    # st.button("find wiki pages")
    # if "wiki_suggestions" in st.session_state:
    #         st.button("generate", on_click=generate_graph, key="gen_graph")
    pass
else:
    if len(st.session_state['wiki_text']) > 0:
        st.button("Generate", on_click=generate_graph, key="gen_graph")


if st.session_state['has_run']:
    st.sidebar.markdown(
    """
# How to expand the graph
- Click a button on the right to expand that node
- Only nodes that have wiki pages will be expanded
- Hit the Generate button again to expand your graph!
"""
)

    cols = st.columns([5, 1])
    with cols[0]:
        HtmlFile = open(network_filename, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, height=2000,width=2000)
    with cols[1]:
        for i,s in enumerate(st.session_state["nodes"]):
            st.button(s, on_click=add_text, args=(s,), key=s+str(i))






