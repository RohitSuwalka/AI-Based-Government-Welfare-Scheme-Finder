import json
import pathlib

import streamlit as st

from recommender import get_recommendations
from districts import DISTRICTS, STATES

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Welfare Scheme Finder",
    page_icon="🏛️",
    layout="wide",
)

CATEGORY_COLORS = {
    "Agriculture": "#2d6a4f",
    "Housing": "#1d3557",
    "Financial Inclusion": "#457b9d",
    "Social Security": "#6d4c41",
    "Insurance": "#00695c",
    "Health": "#c62828",
    "Education": "#6a1b9a",
    "Women and Child Welfare": "#ad1457",
    "Entrepreneurship": "#e65100",
    "Employment": "#1565c0",
    "Disability": "#558b2f",
    "Rural Development": "#4527a0",
}


# ── Data loader ───────────────────────────────────────────────────────────────
@st.cache_data
def load_schemes() -> list:
    data_path = pathlib.Path(__file__).parent / "schemes.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Why-it-matches generator ──────────────────────────────────────────────────
def build_match_reason(profile: dict, scheme: dict) -> str:
    parts = []

    age = profile.get("age")
    gender = profile.get("gender", "")
    occupation = profile.get("occupation", "")
    category = profile.get("category", "")
    income = profile.get("income")
    state = profile.get("state", "")
    special_status = profile.get("special_status", [])
    category_name = scheme.get("category", "")

    if age:
        parts.append(f"a {age}-year-old")
    if gender and gender != "Prefer not to say":
        parts.append(gender.lower())
    if occupation and occupation != "Other":
        parts.append(occupation.lower())
    if state:
        parts.append(f"from {state}")
    if category and category != "General":
        parts.append(f"in the {category} category")
    if income is not None:
        parts.append(f"with an annual household income of ₹{income:,}")

    status_phrases = {
        "Differently Abled": "a differently abled person",
        "BPL Card Holder": "a BPL card holder",
        "Pregnant or Lactating": "pregnant or lactating",
        "Widow": "a widow",
        "Senior Citizen": "a senior citizen",
        "Veteran / Ex-Serviceman": "a veteran or ex-serviceman",
    }
    for status in special_status:
        if status in status_phrases:
            parts.append(status_phrases[status])

    profile_str = ", ".join(parts) if parts else "your profile"
    return (
        f"As {profile_str}, you may be eligible for this "
        f"**{category_name}** scheme. "
        f"Your profile matches the eligibility keywords for this programme."
    )


# ── Score badge helper ────────────────────────────────────────────────────────
def score_badge(score: float) -> str:
    if score >= 60:
        color = "#2d6a4f"
    elif score >= 35:
        color = "#e65100"
    else:
        color = "#888"
    return (
        f'<span style="background:{color};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:0.85em;font-weight:600;">'
        f"Match: {score}%</span>"
    )


# ── Compact header CSS ────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    h1 { margin-bottom: 0.1rem !important; font-size: 1.8rem !important; }
    h1 + div p { margin-top: 0 !important; margin-bottom: 0.4rem !important; }
    hr { margin-top: 0.4rem !important; margin-bottom: 0.6rem !important; }
    [data-testid="stSidebar"] h2 { margin-top: -0.5rem !important; padding-top: 0 !important; margin-bottom: 0.1rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🏛️ Government Welfare Scheme Finder")
st.markdown("Enter your details to discover government schemes you may be eligible for.")
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
if "profile_snapshot" not in st.session_state:
    st.session_state.profile_snapshot = None

# ── Sidebar — profile form ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Your Profile")
    # Widgets are outside st.form so district updates instantly on state change.
    # Results only refresh when the button is clicked.
    age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
    gender = st.selectbox("Gender", ["— Select —", "Male", "Female", "Other", "Prefer not to say"])
    state = st.selectbox("State / Union Territory", ["— Select State —"] + sorted(STATES))
    district_options = (
        ["— Select District —"] + DISTRICTS.get(state, [])
        if state != "— Select State —"
        else ["— Select District —"]
    )
    district = st.selectbox("District", district_options)
    income = st.number_input(
        "Annual Household Income (₹)",
        min_value=0,
        max_value=10_000_000,
        value=0,
        step=5_000,
        help="Total income of all earning members in your household per year",
    )
    occupation = st.selectbox(
        "Occupation",
        ["Farmer", "Student", "Salaried", "Self-Employed", "Unemployed", "Other"],
    )
    category = st.selectbox(
        "Social Category",
        ["General", "OBC", "SC", "ST", "Minority"],
    )
    with st.expander("Special Status (select all that apply)"):
        _ss_student    = st.checkbox("Student")
        _ss_farmer     = st.checkbox("Farmer")
        _ss_disabled   = st.checkbox("Differently Abled")
        _ss_bpl        = st.checkbox("BPL Card Holder")
        _ss_pregnant   = st.checkbox("Pregnant or Lactating")
        _ss_widow      = st.checkbox("Widow")
        _ss_senior     = st.checkbox("Senior Citizen")
        _ss_veteran    = st.checkbox("Veteran / Ex-Serviceman")
    special_status = [
        label for label, checked in [
            ("Student",               _ss_student),
            ("Farmer",                _ss_farmer),
            ("Differently Abled",     _ss_disabled),
            ("BPL Card Holder",       _ss_bpl),
            ("Pregnant or Lactating", _ss_pregnant),
            ("Widow",                 _ss_widow),
            ("Senior Citizen",        _ss_senior),
            ("Veteran / Ex-Serviceman", _ss_veteran),
        ]
        if checked
    ]
    description = st.text_area(
        "Describe your situation (optional)",
        placeholder="e.g. I am a small farmer with 2 acres of land and have a disabled child...",
        height=100,
    )
    st.divider()
    if st.button("🔍 Find Schemes", use_container_width=True, type="primary"):
        errors = []
        if age <= 0:
            errors.append("⚠️ Please enter your Age.")
        if gender == "— Select —":
            errors.append("⚠️ Please select your Gender.")
        if state == "— Select State —":
            errors.append("⚠️ Please select your State.")
        if district == "— Select District —":
            errors.append("⚠️ Please select your District.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.profile_snapshot = {
                "age": int(age),
                "gender": gender,
                "state": state,
                "district": district,
                "income": int(income),
                "occupation": occupation,
                "category": category,
                "special_status": special_status,
                "description": description,
            }

# ── Main area — results ───────────────────────────────────────────────────────
st.subheader("Recommended Schemes")

if st.session_state.profile_snapshot is None:
    st.info(
        "Fill in your profile in the sidebar on the left and click **Find Schemes** "
        "to see personalised recommendations."
    )
else:
    schemes = load_schemes()
    profile = st.session_state.profile_snapshot

    with st.spinner("Matching your profile against schemes..."):
        results = get_recommendations(profile, schemes, top_n=5)

    if not results:
        st.warning("No schemes found. Try broadening your profile details.")
    else:
        st.success(f"**{len(results)} schemes match your profile.**")

        for rank, scheme in enumerate(results, start=1):
            score = scheme.get("match_score", 0)
            cat = scheme.get("category", "")
            cat_color = CATEGORY_COLORS.get(cat, "#555")
            header_label = f"#{rank}  {scheme['name']}  —  {cat}"

            with st.expander(header_label, expanded=(rank == 1)):
                # Score + category pill row
                st.markdown(
                    score_badge(score)
                    + f'&nbsp;&nbsp;<span style="background:{cat_color};color:#fff;'
                    f'padding:3px 10px;border-radius:12px;font-size:0.85em;">'
                    f"{cat}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("")

                # Why it matches
                st.markdown("**🎯 Why it matches you**")
                st.markdown(build_match_reason(profile, scheme))
                st.markdown("")

                # Benefits
                st.markdown("**💰 Benefits**")
                st.markdown(scheme.get("benefits", "N/A"))
                st.markdown("")

                # Eligibility criteria
                st.markdown("**✅ Eligibility Criteria**")
                for criterion in scheme.get("eligibility_criteria", []):
                    st.markdown(f"- {criterion}")
                st.markdown("")

                # Required documents
                st.markdown("**📄 Required Documents**")
                docs = scheme.get("required_documents", [])
                cols = st.columns(2)
                for i, doc in enumerate(docs):
                    cols[i % 2].markdown(f"- {doc}")
                st.markdown("")

                # How to apply
                st.markdown("**📝 How to Apply**")
                st.markdown(scheme.get("how_to_apply", "N/A"))
                st.markdown("")

                # Official source
                source_url = scheme.get("source_url", "")
                if source_url:
                    st.markdown(
                        f"**🔗 Official Source:** [{source_url}]({source_url})"
                    )

    st.markdown("")
    st.caption(f"Searching across {len(load_schemes())} government schemes.")
