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
    'wiki_suggestions': "",
    'wiki_text' : [],
    'nodes':[]
}

for k, v in state_variables.items():
    if k not in st.session_state:
        st.session_state[k] = v

def clip_text(t, lenght = 5):
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
    reset_session()
    with st.spinner(text="fetching wiki topics..."):
        if st.session_state['input_method'] == "wikipedia":
            text = st.session_state.text
            if text is not None:
                st.session_state['wiki_suggestions'] = wikipedia.search(text, results = 3)

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
    except wikipedia.DisambiguationError as e:
        st.session_state["nodes"].remove(term)

def reset_session():
    for k in state_variables:
        del st.session_state[k]

st.title('REBELious knowledge graph generation')
st.session_state['input_method'] = "wikipedia"

# st.selectbox(
#      'input method',
#      ('wikipedia', 'free text'),  key="input_method")

if st.session_state['input_method'] != "wikipedia":
    # st.text_area("Your text", key="text")
    pass
else:
    st.text_input("wikipedia search term",on_change=show_suggestion, key="text")

if len(st.session_state['wiki_suggestions']) != 0:
    columns = st.columns([1] * len(st.session_state['wiki_suggestions']))
    for i, (c, s) in enumerate(zip(columns, st.session_state['wiki_suggestions'])):
        with c:
            st.button(s, on_click=show_wiki_text, args=(s,), key=str(i)+s)

if len(st.session_state['wiki_text']) != 0:
    for t in st.session_state['wiki_text']:
        new_expander = st.expander(label=t[:30] + "...")
        with new_expander:
            st.markdown(t)

if st.session_state['input_method'] != "wikipedia":
    # st.button("find wiki pages")
    # if "wiki_suggestions" in st.session_state:
    #         st.button("generate", on_click=generate_graph, key="gen_graph")
    pass
else:
    st.button("generate", on_click=generate_graph, key="gen_graph")


if st.session_state['has_run']:
    cols = st.columns([4, 1])
    with cols[0]:
        HtmlFile = open(network_filename, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, height=1500,width=1500)
    with cols[1]:
        st.text("expand")
        for i,s in enumerate(st.session_state["nodes"]):
            st.button(s, on_click=add_text, args=(s,), key=s+str(i))






