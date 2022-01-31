from typing import List
from transformers import pipeline
from pyvis.network import Network
from functools import lru_cache
import spacy
from spacy import displacy


DEFAULT_LABEL_COLORS = {
    "ORG": "#7aecec",
    "PRODUCT": "#bfeeb7",
    "GPE": "#feca74",
    "LOC": "#ff9561",
    "PERSON": "#aa9cfc",
    "NORP": "#c887fb",
    "FACILITY": "#9cc9cc",
    "EVENT": "#ffeb80",
    "LAW": "#ff8197",
    "LANGUAGE": "#ff8197",
    "WORK_OF_ART": "#f0d0ff",
    "DATE": "#bfe1d9",
    "TIME": "#bfe1d9",
    "MONEY": "#e4e7d2",
    "QUANTITY": "#e4e7d2",
    "ORDINAL": "#e4e7d2",
    "CARDINAL": "#e4e7d2",
    "PERCENT": "#e4e7d2",
}

def generate_knowledge_graph(texts: List[str], filename: str):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("\n".join(texts).lower())
    NERs = [ent.text for ent in doc.ents]
    NER_types =  [ent.label_ for ent in doc.ents]

    triplets = []
    for triplet in texts:
        triplets.extend(generate_partial_graph(triplet))
    heads = [ t["head"].lower() for t in triplets]
    tails = [ t["tail"].lower() for t in triplets]

    nodes = list(set(heads + tails))
    net = Network(directed=True, width="700px", height="700px")

    for n in nodes:
        if n in NERs:
            NER_type = NER_types[NERs.index(n)]
            if NER_type in NER_types:
                if NER_type in DEFAULT_LABEL_COLORS.keys():
                    color = DEFAULT_LABEL_COLORS[NER_type]
                else:
                    color = "#666666"
                net.add_node(n, title=NER_type, shape="circle", color=color)
            else:
                net.add_node(n, shape="circle")
        else:
            net.add_node(n, shape="circle")

    unique_triplets = set()
    stringify_trip = lambda x : x["tail"] + x["head"] + x["type"].lower()
    for triplet in triplets:
        if stringify_trip(triplet) not in unique_triplets:
            net.add_edge(triplet["head"].lower(), triplet["tail"].lower(),
                         title=triplet["type"], label=triplet["type"])
            unique_triplets.add(stringify_trip(triplet))

    net.repulsion(
        node_distance=200,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )
    net.set_edge_smooth('dynamic')
    net.show(filename)
    return nodes


@lru_cache(maxsize=16)
def generate_partial_graph(text: str):
    triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')
    a = triplet_extractor(text, return_tensors=True, return_text=False)[0]["generated_token_ids"]["output_ids"]
    extracted_text = triplet_extractor.tokenizer.batch_decode(a)
    extracted_triplets = extract_triplets(extracted_text[0])
    return extracted_triplets


def extract_triplets(text):
    """
    Function to parse the generated text and extract the triplets
    """
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})

    return triplets

