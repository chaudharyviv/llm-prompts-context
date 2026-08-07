# Workshop AI Toolkit

Unified Streamlit application that merges two workshop demos into a single multi-mode app:

| Mode | Origin | Model | Purpose |
|------|--------|-------|---------|
| **Persona Chatbot** | Week 1 | Anthropic Claude (`claude-haiku-4-5`) | Chat with six distinct system-prompt personas |
| **Resume Scanner Pro** | Week 2 | OpenAI (`gpt-4o-mini`) | Score a resume against a job description with clear decision reasoning |

Switch between modes from the sidebar radio button. Each mode keeps its own session state (chat history, temperature, loaded samples, etc.).

---

## Features

### 🎭 Persona Chatbot

Six ready-to-use personas with carefully engineered system prompts:

| Persona | Character |
|---------|-----------|
| Infrastructure Engineer | Senior infra (Linux, storage, K8s, cloud) — blunt, failure-mode focused |
| Software Engineer | Python / APIs / distributed systems — code-first explanations |
| Startup Founder | Berlin B2B SaaS founder — GDPR, GmbH, BaFin, German employment law |
| Socratic Teacher | Never gives direct answers; only guiding questions |
| UK Lawyer | London commercial / tech solicitor — jurisdiction-aware, heavy caveats |
| Junior Analyst | First-year analyst — honest uncertainty, learning in public |

- Per-persona conversation history
- Temperature slider (0.0–1.0)
- Suggested starter questions for each persona
- System prompt visible in the UI for teaching / inspection
- Clear chat button

### 🎯 Resume Scanner Pro (Week 2)

- Pre-loaded job descriptions (Linux Engineer, Software Engineer) + custom JD paste
- Four sample resumes (strong / weak for each role) + free-text resume area
- Structured evaluation:
  - Overall score (1–10) + verdict (`SELECTED` / `MANAGER REVIEW` / `NOT SELECTED`)
  - Category scores (Technical Skills, Experience, Education & Certifications, Soft Skills)
  - Strengths & Gaps lists
  - Explicit **“Why This Decision?”** recommendation box
  - Full raw justification expander
  - JSON download of the evaluation report
- Independent temperature control for the scoring model

---

## Project layout

```
.
├── workshop_app.py      # Single entry-point Streamlit app (both modes)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

Original separate scripts (for reference only):

- `chatbot_w01_personas.py`
- `w02_prompt_context.py`

---

## Prerequisites

- Python 3.10+
- An Anthropic API key (for Persona Chatbot)
- An OpenAI API key (for Resume Scanner)

You can run either mode if only one key is present; the missing key simply disables that mode with a sidebar warning.

---

## Installation

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Secrets configuration

Create a Streamlit secrets file:

```bash
mkdir -p .streamlit
```

Edit `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY    = "sk-..."
```

**Never commit this file.** Add `.streamlit/secrets.toml` to your `.gitignore`.

---

## Running the app

```bash
streamlit run workshop_app.py
```

The app opens in your browser (default `http://localhost:8501`).

1. Use the **App Mode** radio in the sidebar to choose **Persona Chatbot** or **Resume Scanner**.
2. Persona mode: pick a persona, adjust temperature, type a message or click a suggested question.
3. Resume mode: select a job role, load (or paste) a resume, click **Evaluate Candidate**.

---

## How the merge works

| Concern | Approach |
|---------|----------|
| Entry point | Single `workshop_app.py` |
| Navigation | Sidebar radio → `st.session_state.app_mode` |
| Shared CSS | Combined stylesheet covering both UIs |
| API clients | Separate cached clients (`get_anthropic_client`, `get_openai_client`) |
| Session state | Namespaced keys so the two modes do not overwrite each other |
| UI isolation | Large `if / else` blocks for main content; mode-specific controls only rendered in the matching sidebar branch |

No multi-page folder structure is required — everything lives in one file for easy workshop distribution.

---

## Model notes & caveats

- **Persona Chatbot** uses `claude-sonnet-4-6`. If that model ID is unavailable in your account, change the `model=` argument in the `client.messages.create(...)` call.
- **Resume Scanner** uses `gpt-4o-mini` for cost-efficient, structured scoring. You can swap it for another chat model that supports the same messages API.
- Temperature for personas defaults to `0.7` (more creative). Temperature for resume scoring defaults to `0.1` (more deterministic).
- The Resume Scanner system prompt enforces a strict output format so the regex parser can extract scores, verdict, strengths, and gaps. If you edit the system prompt, update the parser accordingly.
- The UK Lawyer persona always includes a legal-advice disclaimer; treat its output as educational only.

---

## Extending the app

**Add a new persona**

1. Append an entry to the `PERSONAS` dict (emoji, name, role, user_label, system prompt).
2. Optionally add starter questions to `SUGGESTED_PROMPTS`.
3. Chat history is initialised automatically from the keys of `PERSONAS`.

**Add a new job description or sample resume**

1. Extend `JOB_DESCRIPTIONS` or `SAMPLE_RESUMES`.
2. The sidebar radio / selectbox pick them up automatically.

**Change models**

Search for `model=` in `workshop_app.py` and replace the string.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| “ANTHROPIC_API_KEY not found” | Missing or misnamed secret | Check `.streamlit/secrets.toml` |
| “OpenAI client not initialized” | Same for OpenAI | Same |
| API Error / rate limit | Key quota or network | Verify key, wait, or lower max_tokens |
| Parser shows score 0 / ERROR | Model ignored the required format | Lower temperature or tighten the system prompt |
| Suggested buttons do nothing | Form vs. button interaction | Click a suggested question; it programmatically sets `user_input` and triggers the same path as the form |

---

## License & usage

Workshop / educational material. API keys and costs are the responsibility of the person running the app. Do not use the Resume Scanner output as the sole basis for real hiring decisions without human review.
