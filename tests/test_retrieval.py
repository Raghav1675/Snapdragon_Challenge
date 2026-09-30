from aura.retrieval import LocalRetriever


def test_local_retrieval():
    r = LocalRetriever([
        ("Photosynthesis uses sunlight to produce chemical energy in plants.", "science.txt"),
        ("HTTP is an application protocol used for web communication.", "web.txt"),
    ])
    hits = r.search("plants sunlight", 1)
    assert hits
    assert hits[0].source == "science.txt"
