"""Applicant-name harmonisation methods compared in Step 2.

A        dictionary of legal forms (the method used so far in 11_exercise.ipynb)
A+       A + Unicode normalisation, abbreviations (UNIV -> UNIVERSITY ...), filler words, non-Latin fallback
B        cleanco, then A
first    first word of the A-cleaned name (called "method C" in 11_exercise.ipynb; NOT Terrorizer)
T        Terrorizer (Ascione, https://github.com/graziasveva/Terrorizer), re-implemented here

Why a re-implementation of Terrorizer: the package is not on PyPI, and the repository code cannot be run as it is
(the `terrorizer_disambiguator` function of the README is missing; `get_vector` returns only the last vector;
`get_idf` re-applies the log inside the loop; the >1000-names branch uses an undefined variable). We keep its four
stages and its scoring rule:

  1. preprocessing: lower-case, drop text in brackets and commas, remove legal forms (cleanco), punctuation -> space;
  2. (optional) knowledge augmentation with a web-crawled knowledge base: NOT used (the base is a separate download
     and its domain/url features are rarely available for our names);
  3. matching: score(i, j) = w_similarity * cosine(v_i, v_j) + w_shared_token * [i, j share a token]
                             + w_first_token * [same first token];
     v = average of the word embeddings of the name ("Vsevolod/company-names-similarity-sentence-transformer"),
     weighted by the word's IDF (rare, distinctive words weigh more: our reading of `total_score`);
     an edge links i and j when score >= match_threshold;
  4. network: remove the edges of the nodes whose bridgeness centrality > bridgeness_threshold (nodes that join two
     groups), Louvain communities (resolution), then the same refinement inside each community.
     Each community = one applicant.
"""

import re
import unicodedata

import networkx as nx
import numpy as np
from cleanco import basename

# ---------------------------------------------------------------- method A (as in 11_exercise.ipynb)
LEGAL_FORMS = {
    "INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "LLC", "LP", "PLC",
    "GMBH", "AG", "KG", "MBH", "SE", "SA", "SAS", "SPA", "SRL", "BV", "NV", "AB", "AS", "ASA", "OY", "OYJ",
    "KK", "KABUSHIKI", "KAISHA", "LTDA", "PTY", "THE", "AKTIENGESELLSCHAFT", "GESELLSCHAFT",
}


def clean_a(name):
    "Method A: upper-case, keep letters/digits, drop legal-form words at the start and end."
    words = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper()).split()
    while words and words[-1] in LEGAL_FORMS:
        words.pop()
    while words and words[0] in LEGAL_FORMS:
        words.pop(0)
    return " ".join(words)


# ---------------------------------------------------------------- method A+ (step 1 proposal)
ABBREVIATIONS = {
    "UNIV": "UNIVERSITY", "INST": "INSTITUTE", "SCI": "SCIENCE", "TECH": "TECHNOLOGY",
    "TECHNOL": "TECHNOLOGY", "ENG": "ENGINEERING", "RES": "RESEARCH", "NATL": "NATIONAL",
}
FILLER_WORDS = {"OF", "AND", "THE"}


def clean_a_plus(name):
    "Method A+: A with Unicode normalisation, abbreviations, filler words and a fallback for non-Latin names."
    text = unicodedata.normalize("NFKC", str(name)).upper()
    words = re.sub(r"[^A-Z0-9 ]", " ", text).split()
    words = [ABBREVIATIONS.get(w, w) for w in words if w not in FILLER_WORDS]
    while words and words[-1] in LEGAL_FORMS:
        words.pop()
    while words and words[0] in LEGAL_FORMS:
        words.pop(0)
    cleaned = " ".join(words)
    if len(cleaned) < 3:
        return str(name).strip()
    return cleaned


def clean_b(name):
    "Method B: cleanco, then A."
    return clean_a(basename(str(name)))


def first_word(name):
    "First word of the A-cleaned name."
    words = clean_a(name).split()
    return words[0] if words else ""


# ---------------------------------------------------------------- Terrorizer
MODEL_NAME = "Vsevolod/company-names-similarity-sentence-transformer"


def terrorizer_normalise(name):
    "Stage 1 of Terrorizer (preprocess + _clean_text): lower, no brackets/commas, cleanco, punctuation -> space."
    text = unicodedata.normalize("NFKC", str(name)).lower().replace(",", " ")
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = basename(text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    words = text.split()
    if len(words) > 1 and words[0].isnumeric():          # join_num_text: "3 m" -> "3m"
        words = [words[0] + words[1]] + words[2:]
    return " ".join(words)


def bridgeness_centrality(G):
    """Bridgeness centrality (Jensen et al. 2016; code of M. Morini used by Terrorizer): like betweenness, but only
    shortest paths between nodes at distance > 1 count, and the end points' own contribution is left out.
    Computed per connected component (paths never leave a component), normalised by the size of the whole graph."""
    n = G.number_of_nodes()
    bridgeness = dict.fromkeys(G, 0.0)
    for component in nx.connected_components(G):
        if len(component) < 3:
            continue
        H = G.subgraph(component)
        for s in H:
            # BFS shortest paths from s
            order, preds, sigma, dist = [], {v: [] for v in H}, dict.fromkeys(H, 0.0), {s: 0}
            sigma[s] = 1.0
            queue = [s]
            head = 0
            while head < len(queue):
                v = queue[head]
                head += 1
                order.append(v)
                for w in H[v]:
                    if w not in dist:
                        dist[w] = dist[v] + 1
                        queue.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        preds[w].append(v)
            # accumulation (bridgeness version: no +1 for the end point)
            delta = dict.fromkeys(order, 0.0)
            delta_bri = dict.fromkeys(order, 0.0)
            while order:
                w = order.pop()
                coeff = (1.0 + delta[w]) / sigma[w]
                coeff_bri = delta[w] / sigma[w]
                for v in preds[w]:
                    delta[v] += sigma[v] * coeff
                    delta_bri[v] += sigma[v] * coeff_bri
                if dist[w] > 1:
                    bridgeness[w] += delta_bri[w]
    if n > 2:
        scale = 1.0 / ((n - 1) * (n - 2))
        bridgeness = {v: b * scale for v, b in bridgeness.items()}
    return bridgeness


class Terrorizer:
    "Terrorizer re-implementation: prepare() once per list of names, then cluster() with any parameters."

    def __init__(self, model_name=MODEL_NAME):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self._word_vectors = {}

    def _vectors_of(self, words):
        missing = [w for w in words if w not in self._word_vectors]
        if missing:
            encoded = self.model.encode(missing, batch_size=256, show_progress_bar=False)
            self._word_vectors.update(zip(missing, encoded))
        return [self._word_vectors[w] for w in words]

    def prepare(self, names):
        "Pairwise features of a list of names: cosine similarity, shared token, same first token."
        normalised = [terrorizer_normalise(n) for n in names]
        tokens = [s.split() for s in normalised]
        vocabulary = sorted({w for t in tokens for w in t})
        index = {w: i for i, w in enumerate(vocabulary)}
        n_docs = len(names)
        doc_freq = np.zeros(len(vocabulary))
        X = np.zeros((n_docs, len(vocabulary)), dtype=np.float32)
        for d, t in enumerate(tokens):
            for w in set(t):
                X[d, index[w]] = 1.0
        doc_freq = X.sum(axis=0)
        idf = np.log(n_docs / doc_freq)
        idf_of = dict(zip(vocabulary, idf))

        word_vec = dict(zip(vocabulary, self._vectors_of(vocabulary)))
        dim = self.model.get_sentence_embedding_dimension()
        V = np.zeros((n_docs, dim), dtype=np.float32)
        for d, t in enumerate(tokens):
            if t:
                weights = np.array([idf_of[w] + 1e-4 for w in t])
                V[d] = np.average([word_vec[w] for w in t], axis=0, weights=weights)
        norms = np.linalg.norm(V, axis=1, keepdims=True)
        V = np.divide(V, norms, out=np.zeros_like(V), where=norms > 0)

        first = np.array([t[0] if t else f"__empty{d}" for d, t in enumerate(tokens)])
        return {
            "names": list(names),
            "normalised": normalised,
            "cosine": V @ V.T,
            "shared_token": (X @ X.T) > 0,
            "first_token": first[:, None] == first[None, :],
        }

    @staticmethod
    def cluster(features, w_similarity=1.0, w_shared_token=0.1, w_first_token=0.2, match_threshold=0.9,
                resolution=1.0, bridgeness_threshold=None, seed=0):
        "Stages 3-4: score matrix -> graph -> bridgeness pruning -> Louvain (+ refinement). Returns group labels."
        score = (w_similarity * features["cosine"]
                 + w_shared_token * features["shared_token"]
                 + w_first_token * features["first_token"])
        n = len(features["names"])
        i, j = np.where(np.triu(score >= match_threshold, k=1))
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_weighted_edges_from(zip(i.tolist(), j.tolist(), score[i, j].tolist()))

        def prune(graph):
            if bridgeness_threshold is None:
                return graph
            graph = nx.Graph(graph)
            for v, b in bridgeness_centrality(graph).items():
                if b > bridgeness_threshold:
                    graph.remove_edges_from(list(graph.edges(v)))
            return graph

        G = prune(G)
        communities = nx.community.louvain_communities(G, resolution=resolution, seed=seed)
        final = []
        for community in communities:
            if len(community) <= 2 or bridgeness_threshold is None:
                final.append(community)
                continue
            sub = prune(G.subgraph(community))
            final.extend(nx.community.louvain_communities(sub, resolution=resolution, seed=seed))

        labels = np.empty(n, dtype=object)
        for community in final:
            members = sorted(community)
            label = min(features["names"][m] for m in members)   # as Terrorizer: alphabetically first name
            for m in members:
                labels[m] = label
        return list(labels)
