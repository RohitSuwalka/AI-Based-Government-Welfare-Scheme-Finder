# AI-Based Welfare Scheme Recommendation System — Plan

## Top-Level Overview

**Goal:** Build a simple, fully offline, English-only Streamlit app that collects a user's personal profile and uses TF-IDF + cosine similarity to recommend the top 5 most relevant Indian government welfare schemes.

**Stack:**
- Python 3.x
- Streamlit (UI + backend in one file)
- scikit-learn (TF-IDF vectorizer + cosine similarity)
- pandas (data loading)
- JSON as the schemes data store

**Scope:**
- Single-page Streamlit app
- Hand-crafted dataset of 20–40 real Indian government schemes
- No external APIs, no database, no login, no export
- Fully offline and runnable with `streamlit run app.py`

**Non-Goals:**
- Multilingual support
- User accounts or history
- Live data from government portals
- LLM/GPT integration

---

## Project File Structure

```
scheme-recommendation/
├── app.py                   # Main Streamlit app (UI + recommendation logic)
├── schemes.json             # Hand-crafted welfare schemes dataset
├── recommender.py           # TF-IDF + cosine similarity engine
├── requirements.txt         # Python dependencies
└── README.md                # Setup and run instructions
```

---

## Sub-Tasks

---

### Sub-Task 1 — Build the Schemes Dataset (`schemes.json`)

**Status:** [x] done

**Intent:**
Create the core data file that the recommendation engine will match against. Each scheme entry must be rich enough in text that TF-IDF can meaningfully distinguish schemes by eligibility profile.

**Expected Outcomes:**
- `schemes.json` exists with 20–40 real Indian government schemes
- Each entry has all required fields
- Schemes span all major categories: agriculture, education, health, disability, employment, women/child welfare, housing, social security

**Schema per scheme entry:**
```json
{
  "id": "unique_slug",
  "name": "Scheme Name",
  "category": "Education / Agriculture / Health / ...",
  "description": "Plain text description of the scheme and who it targets",
  "eligibility_text": "Free-text eligibility rules used for TF-IDF matching",
  "benefits": "What the beneficiary receives",
  "eligibility_criteria": ["Bullet 1", "Bullet 2"],
  "required_documents": ["Aadhaar", "Income Certificate", ...],
  "how_to_apply": "Step-by-step application instructions",
  "source_url": "https://official-link.gov.in"
}
```

**Key field for ML:** `eligibility_text` — this is the field the TF-IDF vectorizer indexes. It should include all keywords that describe who the scheme is for: age ranges, gender, income level, occupation, caste category, state, disability status, student/farmer/employment status.

**Todo List:**
- [x] Create `schemes.json` with 20–40 schemes covering all major categories
- [x] Ensure `eligibility_text` for each scheme contains rich, descriptive keywords matching user profile fields
- [x] Include real scheme names, real benefit descriptions, and real official URLs
- [x] Validate JSON is well-formed

**Schemes to include (representative list):**
- PM Kisan Samman Nidhi (farmers)
- PM Awas Yojana — Gramin and Urban (housing, low income)
- Pradhan Mantri Jan Dhan Yojana (financial inclusion)
- Atal Pension Yojana (unorganized workers, age 18-40)
- PM Jeevan Jyoti Bima Yojana (life insurance, low income)
- PM Suraksha Bima Yojana (accident insurance)
- Ayushman Bharat PM-JAY (health, low income families)
- National Scholarship Portal schemes (students, SC/ST/OBC/minority)
- Post Matric Scholarship for SC students
- Pre Matric Scholarship for minorities
- Sukanya Samriddhi Yojana (girl child, parents)
- Beti Bachao Beti Padhao (girls, education)
- PM Matru Vandana Yojana (pregnant/lactating women)
- MGNREGA (rural employment, adults)
- PM Rozgar Protsahan Yojana (employers/employees, formal employment)
- Startup India Seed Fund (entrepreneurs)
- Stand-Up India (SC/ST/women entrepreneurs)
- PM MUDRA Yojana (small business, low income)
- National Social Assistance Programme — NSAP (elderly, widow, disability)
- Indira Gandhi National Old Age Pension (elderly, BPL)
- Indira Gandhi National Widow Pension (widows, BPL)
- Indira Gandhi National Disability Pension (disability, BPL)
- Disability Certificate and ADIP Scheme (disability)
- PM Scholarship Scheme for Central Armed Police Forces
- National Apprenticeship Promotion Scheme (youth, skill training)
- PMEGP — PM Employment Generation Programme (unemployed, self-employment)
- Kisan Credit Card (farmers, fishermen)
- PM Fasal Bima Yojana (farmers, crop insurance)
- Soil Health Card Scheme (farmers)
- e-NAM (farmers, market access)

---

### Sub-Task 2 — Build the Recommendation Engine (`recommender.py`)

**Status:** [x] done

**Intent:**
Implement the core ML logic that converts a user profile dict into a ranked list of matching schemes using TF-IDF vectorization and cosine similarity.

**Expected Outcomes:**
- `recommender.py` exports a single function `get_recommendations(user_profile: dict, schemes: list, top_n: int = 5) -> list`
- Returns top N schemes sorted by descending match score
- Each result includes the scheme dict + a `match_score` float (0–100, percentage)

**How it works:**
1. Load all `eligibility_text` values from schemes as the TF-IDF corpus
2. Convert the user profile dict into a single descriptive query string (e.g. `"age 45 male farmer Karnataka annual income 80000 SC category disability"`)
3. Fit TF-IDF on the corpus + query together, then compute cosine similarity between the query vector and each scheme vector
4. Return top N results with scores

**Todo List:**
- [x] Create `recommender.py`
- [x] Implement `build_user_query(profile: dict) -> str` — converts user profile fields into a flat keyword string
- [x] Implement `get_recommendations(user_profile, schemes, top_n=5) -> list` using `TfidfVectorizer` + `cosine_similarity` from scikit-learn
- [x] Normalize score to 0–100 range (re-scaled so top match = 100%)
- [x] Return list of dicts: original scheme fields + `match_score`

**Relevant libraries:** `sklearn.feature_extraction.text.TfidfVectorizer`, `sklearn.metrics.pairwise.cosine_similarity`

---

### Sub-Task 3 — Build the Streamlit App (`app.py`)

**Status:** [x] done

**Intent:**
Create the single-page Streamlit UI that collects the user profile, calls the recommendation engine, and displays results in a clear, structured format.

**Expected Outcomes:**
- `app.py` runs with `streamlit run app.py` with no errors
- Form collects all required profile fields
- On submit, displays top 5 scheme recommendations
- Each recommendation card shows: scheme name, match score, why it matches, benefits, eligibility criteria, required documents, how to apply, and source link

**UI Layout:**

**Section 1 — User Profile Form (sidebar or main column):**
| Field | Widget |
|---|---|
| Age | `st.number_input` (1–120) |
| Gender | `st.selectbox` (Male / Female / Other) |
| State | `st.selectbox` (all Indian states) |
| District | `st.text_input` |
| Annual Household Income (₹) | `st.number_input` |
| Occupation | `st.selectbox` (Farmer / Student / Salaried / Self-Employed / Unemployed / Other) |
| Social Category | `st.selectbox` (General / OBC / SC / ST / Minority) |
| Special Status | `st.multiselect` (Student / Farmer / Differently Abled / BPL Card Holder / Pregnant or Lactating / Widow / Senior Citizen / Veteran) |
| Situation Description (optional) | `st.text_area` |

**Section 2 — Results:**
- Show top 5 scheme cards using `st.expander` (collapsed by default, scheme name + score in header)
- Inside each expander: structured sections for all 7 output fields
- Match score shown as a percentage badge
- "Why it matches" section: auto-generated sentence derived from the user profile + scheme category (simple template string, not LLM)

**Todo List:**
- [x] Create `app.py`
- [x] Add page config: title, icon, wide layout
- [x] Build the profile input form (sidebar, reactive district dropdown, checkboxes in expander)
- [x] Load `schemes.json` (cached with `@st.cache_data`)
- [x] On form submit, call `get_recommendations()` from `recommender.py`
- [x] Render top 5 results as expander cards with all required fields
- [x] Add a "Why it matches" template string generator based on user profile fields and scheme category
- [x] Add basic "no results" / "fill in the form" state handling
- [x] Add input validation before search
- [x] Add session state snapshot so results only update on button click

---

### Sub-Task 4 — Dependencies and README

**Status:** [x] done

**Intent:**
Provide the dependency file and documentation so the project can be set up and run by anyone with Python installed.

**Expected Outcomes:**
- `requirements.txt` lists all needed packages with no extras
- `README.md` explains what the project does, how to install, and how to run it

**Todo List:**
- [x] Create `requirements.txt` with: `streamlit`, `scikit-learn` (pandas removed — not used)
- [x] Create `README.md` with: project description, setup steps, run command, ML description, updated project structure

---

## Data Flow Summary

```
User fills form
      |
      v
build_user_query(profile) --> "age 24 female student Delhi income 120000 OBC scholarship education"
      |
      v
TF-IDF vectorize [query + all scheme eligibility_text fields]
      |
      v
cosine_similarity(query_vector, scheme_vectors)
      |
      v
Sort by score, take top 5
      |
      v
Render scheme cards in Streamlit
```
