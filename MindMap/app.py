import streamlit as st
import streamlit.components.v1 as components
from streamlit_lottie import st_lottie
import rebel
import wikipedia
from utils import clip_text
from datetime import datetime as dt
import os

MAX_TOPICS = 3

wiki_state_variables = {
    'has_run_wiki': False,
    'wiki_suggestions': [],
    'wiki_text': [],
    'nodes': [],
    "topics": [],
    "html_wiki": ""
}

free_text_state_variables = {
    'has_run_free': False,
    "html_free": ""
}

BUTTON_COLUMS = 4


def wiki_init_state_variables():
    for k in free_text_state_variables.keys():
        if k in st.session_state:
            del st.session_state[k]

    for k, v in wiki_state_variables.items():
        if k not in st.session_state:
            st.session_state[k] = v


def wiki_generate_graph():
    st.session_state["GRAPH_FILENAME"] = str(
        dt.now().timestamp()*1000) + ".html"

    if 'wiki_text' not in st.session_state:
        return
    if len(st.session_state['wiki_text']) == 0:
        st.error("please enter a topic and select a wiki page first")
        return
    with st.spinner(text="Generating graph..."):
        texts = st.session_state['wiki_text']
        st.session_state['nodes'] = []
        nodes = rebel.generate_knowledge_graph(
            texts, st.session_state["GRAPH_FILENAME"])
        HtmlFile = open(
            st.session_state["GRAPH_FILENAME"], 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.session_state["html_wiki"] = source_code
        os.remove(st.session_state["GRAPH_FILENAME"])
        for n in nodes:
            n = n.lower()
            if n not in st.session_state['topics']:
                possible_topics = wikipedia.search(n, results=2)
                st.session_state['nodes'].extend(possible_topics)
        st.session_state['nodes'] = list(set(st.session_state['nodes']))
        st.session_state['has_run_wiki'] = True
    st.success('Done!')


def wiki_show_suggestion():
    st.session_state['wiki_suggestions'] = []
    with st.spinner(text="fetching wiki topics..."):
        if st.session_state['input_method'] == "wikipedia":
            text = st.session_state.text
            if (text is not None) and (text != ""):
                subjects = text.split(",")[:MAX_TOPICS]
                for subj in subjects:
                    st.session_state['wiki_suggestions'] += wikipedia.search(
                        subj, results=3)


def wiki_show_text(page_title):
    with st.spinner(text="fetching wiki page..."):
        try:
            page = wikipedia.page(title=page_title, auto_suggest=False)
            st.session_state['wiki_text'].append(clip_text(page.summary))
            st.session_state['topics'].append(page_title.lower())
            st.session_state['wiki_suggestions'].remove(page_title)

        except wikipedia.DisambiguationError as e:
            with st.spinner(text="Woops, ambigious term, recalculating options..."):
                st.session_state['wiki_suggestions'].remove(page_title)
                temp = st.session_state['wiki_suggestions'] + e.options[:3]
                st.session_state['wiki_suggestions'] = list(set(temp))
        except wikipedia.WikipediaException:
            st.session_state['wiki_suggestions'].remove(page_title)


def wiki_add_text(term):
    if len(st.session_state['wiki_text']) > MAX_TOPICS:
        return
    try:
        page = wikipedia.page(title=term, auto_suggest=False)
        extra_text = clip_text(page.summary)

        st.session_state['wiki_text'].append(extra_text)
        st.session_state['topics'].append(term.lower())
        st.session_state['nodes'].remove(term)

    except wikipedia.DisambiguationError as e:
        with st.spinner(text="Woops, ambigious term, recalculating options..."):
            st.session_state['nodes'].remove(term)
            temp = st.session_state['nodes'] + e.options[:3]
            st.session_state['nodes'] = list(set(temp))
    except wikipedia.WikipediaException as e:
        st.session_state['nodes'].remove(term)


def wiki_reset_session():
    for k in wiki_state_variables:
        del st.session_state[k]


def free_reset_session():
    for k in free_text_state_variables:
        del st.session_state[k]


def free_text_generate():
    st.session_state["GRAPH_FILENAME"] = str(
        dt.now().timestamp()*1000) + ".html"
    text = st.session_state['free_text'][0:100]
    rebel.generate_knowledge_graph([text], st.session_state["GRAPH_FILENAME"])
    HtmlFile = open(st.session_state["GRAPH_FILENAME"], 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    st.session_state["html_free"] = source_code
    os.remove(st.session_state["GRAPH_FILENAME"])
    st.session_state['has_run_free'] = True


def free_text_layout():
    st.text_area("Free text", key="free_text", height=5,
                 value="Tardigrades, known colloquially as water bears or moss piglets, are a phylum of eight-legged segmented micro-animals.")
    st.button("Generate", on_click=free_text_generate,
              key="free_text_generate")


def free_test_init_state_variables():
    for k in wiki_state_variables.keys():
        if k in st.session_state:
            del st.session_state[k]

    for k, v in free_text_state_variables.items():
        if k not in st.session_state:
            st.session_state[k] = v




st.title('MIND-MAP GEN 🧠')
st.lottie("https://lottie.host/5eaa4aff-8359-46d2-a32d-d67813b31b44/wtNdjTRPUW.json", key="user", height="100px")
st.markdown(
    """
### Building Beautiful Knowledge Graphs With REBEL
""")
st.selectbox(
    'input method',
    ('wikipedia', 'free text'),  key="input_method")


def show_wiki_hub_page():

    cols = st.columns([6, 1])
    with cols[0]:
        st.text_input("wikipedia search term", on_change=wiki_show_suggestion,
                      key="text", value="graphs, are, awesome")
    with cols[1]:
        st.text('')
        st.text('')
        st.button("Search", on_click=wiki_show_suggestion,
                  key="show_suggestion_key")

    if len(st.session_state['wiki_suggestions']) != 0:
        num_buttons = len(st.session_state['wiki_suggestions'])
        num_cols = num_buttons if 0 < num_buttons < BUTTON_COLUMS else BUTTON_COLUMS
        columns = st.columns([1] * num_cols)
        for q in range(1 + num_buttons//num_cols):
            for i, (c, s) in enumerate(zip(columns, st.session_state['wiki_suggestions'][q*num_cols: (q+1)*num_cols])):
                with c:
                    st.button(s, on_click=wiki_show_text, args=(
                        s,), key=str(i)+s+"wiki_suggestion")

    if len(st.session_state['wiki_text']) != 0:
        for i, t in enumerate(st.session_state['wiki_text']):
            new_expander = st.expander(label=t[:30] + "...", expanded=(i == 0))
            with new_expander:
                st.markdown(t)

    if len(st.session_state['wiki_text']) > 0:
        st.button("Generate", on_click=wiki_generate_graph, key="gen_graph")
  

    if st.session_state['has_run_wiki']:

        components.html(st.session_state["html_wiki"], width=720, height=600)
        num_buttons = len(st.session_state["nodes"])
        num_cols = num_buttons if 0 < num_buttons < BUTTON_COLUMS else BUTTON_COLUMS
        columns = st.columns([1] * num_cols + [1])

        for q in range(1 + num_buttons//num_cols):
            for i, (c, s) in enumerate(zip(columns, st.session_state["nodes"][q*num_cols: (q+1)*num_cols])):
                with c:
                    st.button(s, on_click=wiki_add_text,
                              args=(s,), key=str(i)+s)


def show_free_text_hub_page():
    st.sidebar.button("Reset", on_click=free_reset_session,
                      key="free_reset_key")
    

    free_text_layout()

    if st.session_state['has_run_free']:
        components.html(st.session_state["html_free"], width=720, height=600)


if st.session_state['input_method'] == "wikipedia":
    wiki_init_state_variables()
    show_wiki_hub_page()
else:
    free_test_init_state_variables()
    show_free_text_hub_page()


