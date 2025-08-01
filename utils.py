from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def fuzzy_match(search_term, title):
    """Fuzzy match: all keywords must appear in title"""
    keywords = search_term.lower().split()
    return all(k in title.lower() for k in keywords)

def is_similar_enough(a, b, threshold=0.6):
    return similar(a, b) >= threshold
