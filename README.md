# 🏛️ AI-Based Welfare Scheme Recommendation System

A simple, fully offline Streamlit web app that recommends relevant Indian government welfare schemes based on a user's personal profile using TF-IDF and cosine similarity.

---

## Features

- Fixed sidebar profile form — stays visible while scrolling through results
- Reactive district dropdown — updates instantly when a state is selected
- States and districts sourced from a complete India-wide dataset (`districts.py`)
- Input validation — blocks search if required fields are not filled
- Matches user profile against 34 real Indian government schemes
- Displays top 5 recommendations with match score, why it matches, benefits, eligibility criteria, required documents, how to apply, and official links
- Match scores normalised — top result always shows 100%, others shown relative to it
- 100% offline — no API keys, no internet required after setup

---

## Setup

**1. Clone or download the project**

```bash
cd "Scheme recommendation"
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # macOS / Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## How the ML Matching Works

1. Each scheme in `schemes.json` has an `eligibility_text` field — a rich keyword string describing who the scheme targets (age, gender, income, occupation, caste category, disability status, etc.).
2. When the user submits their profile, `recommender.py` converts it into a matching keyword query string using `build_user_query()`.
3. `TfidfVectorizer` (from scikit-learn) vectorizes all scheme texts and the user query together.
4. `cosine_similarity` computes a similarity score between the user query vector and each scheme vector.
5. The top 5 schemes by score are returned and displayed.

---

## Project Structure

```
├── app.py            — Streamlit UI (sidebar form + results)
├── recommender.py    — TF-IDF + cosine similarity engine
├── schemes.json      — 34 Indian government schemes dataset
├── districts.py      — Complete India state → districts mapping
├── requirements.txt  — Python dependencies
└── README.md         — This file
```

---

## Schemes Covered

| Category | Examples |
|---|---|
| Agriculture | PM Kisan, KCC, PMFBY, Soil Health Card, e-NAM |
| Education | Post Matric Scholarships (SC/ST/OBC), Minority Scholarships, CAPF Scholarship |
| Health | Ayushman Bharat PM-JAY |
| Housing | PMAY Gramin, PMAY Urban |
| Employment | MGNREGA, PMEGP, DDU-GKY, NAPS, PMRPY |
| Entrepreneurship | Startup India, Stand-Up India, PM MUDRA |
| Women & Child | Sukanya Samriddhi, PMMVY, Beti Bachao Beti Padhao |
| Disability | IGNDPS, ADIP Scheme |
| Social Security | IGNOAPS, IGNWPS, NFBS, Atal Pension |
| Insurance | PMJJBY, PMSBY |
| Financial Inclusion | PM Jan Dhan Yojana |
