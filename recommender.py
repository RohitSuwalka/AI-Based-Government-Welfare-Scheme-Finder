"""
Recommendation engine for the Welfare Scheme Recommendation System.
Uses TF-IDF vectorization and cosine similarity to match a user's
profile against scheme eligibility descriptions.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_user_query(profile: dict) -> str:
    """
    Convert a user profile dictionary into a flat keyword string
    suitable for TF-IDF matching against scheme eligibility_text fields.

    profile keys expected:
        age (int), gender (str), state (str), district (str),
        income (int), occupation (str), category (str),
        special_status (list[str]), description (str)
    """
    parts = []

    age = profile.get("age")
    if age:
        parts.append(f"age {age}")
        if age >= 60:
            parts.append("senior citizen elderly old age")
        if age <= 18:
            parts.append("youth young")
        if 18 <= age <= 40:
            parts.append("adult working age")

    gender = profile.get("gender", "")
    if gender:
        parts.append(gender.lower())
        if gender.lower() == "female":
            parts.append("woman girl")

    state = profile.get("state", "")
    if state:
        parts.append(state.lower())

    district = profile.get("district", "")
    if district:
        parts.append(district.lower())

    income = profile.get("income")
    if income is not None:
        parts.append(f"annual income {income}")
        if income < 50000:
            parts.append("BPL below poverty line very low income poor")
        elif income < 150000:
            parts.append("low income economically weaker section EWS")
        elif income < 300000:
            parts.append("lower income group LIG")
        elif income < 600000:
            parts.append("middle income group MIG")

    occupation = profile.get("occupation", "")
    if occupation:
        parts.append(occupation.lower())
        occ_map = {
            "farmer": "farmer agriculture cultivator crop landholding rural",
            "student": "student education scholarship college school learning",
            "salaried": "salaried employee formal employment EPF worker",
            "self-employed": "self-employed business entrepreneur micro enterprise",
            "unemployed": "unemployed job seeker employment generation skill training",
            "other": "",
        }
        parts.append(occ_map.get(occupation.lower(), occupation.lower()))

    category = profile.get("category", "")
    if category:
        parts.append(category.lower())
        cat_map = {
            "sc": "SC scheduled caste dalit",
            "st": "ST scheduled tribe tribal",
            "obc": "OBC other backward class",
            "minority": "minority Muslim Christian Sikh Buddhist Parsi",
            "general": "general",
        }
        parts.append(cat_map.get(category.lower(), category.lower()))

    special_status = profile.get("special_status", [])
    status_keywords = {
        "Student": "student education scholarship learning",
        "Farmer": "farmer agriculture cultivator crop",
        "Differently Abled": "disability disabled differently abled handicapped assistive device",
        "BPL Card Holder": "BPL below poverty line poor low income",
        "Pregnant or Lactating": "pregnant lactating maternity mother child nutrition",
        "Widow": "widow widowed bereaved woman",
        "Senior Citizen": "senior citizen elderly old age pension",
        "Veteran / Ex-Serviceman": "ex-serviceman veteran armed forces military CAPF",
    }
    for status in special_status:
        if status in status_keywords:
            parts.append(status_keywords[status])

    description = profile.get("description", "")
    if description:
        parts.append(description.lower())

    return " ".join(filter(None, parts))


def get_recommendations(user_profile: dict, schemes: list, top_n: int = 5) -> list:
    """
    Return the top_n most relevant schemes for the given user profile.

    Args:
        user_profile: dict with user form fields
        schemes:      list of scheme dicts loaded from schemes.json
        top_n:        number of results to return (default 5)

    Returns:
        List of scheme dicts sorted by descending match_score,
        each augmented with a 'match_score' key (0–100 float).
    """
    if not schemes:
        return []

    user_query = build_user_query(user_profile)
    if not user_query.strip():
        return []

    # Build corpus: all scheme eligibility_text strings
    corpus = [s.get("eligibility_text", "") for s in schemes]

    # Append user query as the last document
    all_docs = corpus + [user_query]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        min_df=1,
    )
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    # Query vector is the last row
    query_vec = tfidf_matrix[-1]
    scheme_vecs = tfidf_matrix[:-1]

    # Compute cosine similarities between query and each scheme
    similarities = cosine_similarity(query_vec, scheme_vecs).flatten()

    # Re-scale so the best match = 100 and others are shown relative to it.
    # This keeps the ranking identical while making scores feel meaningful.
    max_score = float(similarities.max()) if similarities.max() > 0 else 1.0

    scored = []
    for i, scheme in enumerate(schemes):
        raw = float(similarities[i])
        result = dict(scheme)
        result["match_score"] = round((raw / max_score) * 100, 1)
        scored.append(result)

    # Sort descending by score, return top_n
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored[:top_n]
