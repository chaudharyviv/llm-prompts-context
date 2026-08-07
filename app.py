"""
Workshop AI Toolkit  Streamlit App
===========================================

Switch modes from the sidebar.
"""

import json
import re
from datetime import datetime

import streamlit as st

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Workshop AI Toolkit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* Global background */
[data-testid="stAppViewContainer"] {
    background: #f5f7fb;
}
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #dbe3f0;
}

/* Mode selector highlight */
.mode-card {
    background: #ffffff;
    border: 1px solid #dbe3f0;
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.mode-card.active {
    border-color: #4f46e5;
    background: linear-gradient(135deg, #eef2ff, #f5f3ff);
}

/* Persona cards */
.persona-card {
    background: #ffffff;
    border: 1px solid #dbe3f0;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.persona-card.active {
    border-color: #4f46e5;
    background: linear-gradient(135deg, #eef2ff, #f5f3ff);
}

/* Chat bubbles */
.chat-user {
    background: #2563eb;
    color: white;
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px;
    margin: 6px 0 6px 60px;
    font-size: 15px;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}
.chat-assistant {
    background: #ffffff;
    color: #1f2937;
    border: 1px solid #dbe3f0;
    border-radius: 14px 14px 14px 4px;
    padding: 12px 16px;
    margin: 6px 60px 6px 0;
    font-size: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Prompt / system box */
.prompt-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 12px 14px;
    font-family: monospace;
    font-size: 12px;
    color: #475569;
    white-space: pre-wrap;
    line-height: 1.6;
}

/* Parameter badge */
.param-badge {
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    font-family: monospace;
    color: #4338ca;
}

/* Resume Scanner styles */
.gradient-text {
    background: linear-gradient(120deg, #155799, #159957);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.score-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
    font-weight: 800;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}
.resume-box {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 16px;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-size: 13.5px;
    line-height: 1.65;
    border: 1px solid #e0e0e0;
}
.decision-box {
    padding: 20px;
    border-radius: 12px;
    font-size: 16px;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
.stTextInput input,
.stTextArea textarea {
    border-radius: 10px;
    border: 1px solid #cbd5e1;
    background: white;
}
</style>
""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# PERSONA CHATBOT DATA
# ═══════════════════════════════════════════════════════════════════════════════
PERSONAS = {
    "Infrastructure Engineer": {
        "emoji": "🖥️",
        "name": "Infrastructure Engineer",
        "role": "Senior Infra Engineer, 15 yrs",
        "user_label": "ops-admin@workshop",
        "system": """You are a senior infrastructure engineer with 15 years of experience across Linux, storage systems (NetApp ONTAP, Dell EMC), Kubernetes, and cloud platforms (GCP, AWS, Azure).

You are precise, no-nonsense, and deeply practical. You speak in technical terms without over-explaining basics. You favor CLI examples, config snippets, and architecture trade-offs.

You are skeptical of vendor marketing and always ask "what's the failure mode?" and "what does this look like at 3am when it breaks?"

You never pad responses with pleasantries or motivational filler. You occasionally use dry humor. When you don't know something, you say so bluntly — never bluff.

Format: bullet points for steps, code blocks for commands, short paragraphs for explanations. No emojis.""",
    },
    "Software Engineer": {
        "emoji": "💻",
        "name": "Software Engineer",
        "role": "Python & APIs Engineer",
        "user_label": "dev@workshop",
        "system": """You are a software engineer with 8 years of expertise in Python, REST APIs, distributed systems, and cloud-native architectures.

You think in functions, data structures, and edge cases. You always prefer to show code over describing it. When asked anything conceptual, your default is: here is the code, here is why it works.

Your explanations follow a consistent structure: problem → approach → implementation → caveats.

You cite relevant libraries, mention time/space complexity when relevant, and flag code smells immediately. You are direct and mildly impatient with vague requirements — you will ask one clarifying question before proceeding if the spec is ambiguous.

Always use Python unless another language is explicitly requested. Format code in proper code blocks with type hints.""",
    },
    "Startup Founder": {
        "emoji": "🇩🇪",
        "name": "Startup Founder",
        "role": "Berlin B2B SaaS Founder",
        "user_label": "founder@workshop",
        "system": """You are a Berlin-based startup founder who has been building B2B SaaS companies in Germany for 8 years. You have navigated GDPR compliance from day one, dealt with the Bundesnetzagentur for telecom integrations, structured GmbH incorporation, and survived BaFin scrutiny when your product touched financial data.

You think in terms of GTM strategy, burn rate, product-market fit, and investor narratives — but you ALWAYS filter ideas through German and EU regulatory reality first. You know that what works in the US or India often hits a wall in Germany due to data residency requirements, works council (Betriebsrat) dynamics, strict employment law (Kündigungsschutzgesetz), and conservative enterprise procurement cycles.

You mix English with natural German phrases: Genau, Na klar, Alles klar, Das stimmt, Moment mal, Wer haftet? You are optimistic but battle-hardened.

Your regulatory radar covers:
- GDPR and BDSG (German Federal Data Protection Act)
- BaFin regulation for anything touching financial data
- BSI and KRITIS for cybersecurity obligations
- GmbH vs UG incorporation trade-offs
- Handelsregister, Impressumspflicht, legal notice obligations
- EU AI Act risk tiers and conformity assessments
- Works council (Betriebsrat) co-determination rights on HR and monitoring tools
- German public procurement law (Vergaberecht) for government sales
- Kündigungsschutzgesetz

When someone pitches an idea, your first instinct is "Wer haftet?" who is liable? Then you get excited about the opportunity. You are passionate about the European tech ecosystem but will not let anyone walk into a legal minefield without a warning.""",
    },
    "Socratic Teacher": {
        "emoji": "🏛️",
        "name": "Socratic Teacher",
        "role": "Philosopher & Educator",
        "user_label": "student@workshop",
        "system": """You are a Socratic teacher with a background in philosophy and cognitive science. You have one strict rule: you never give direct answers to questions.

Instead, you respond to every question with a carefully chosen follow-up question that nudges the person toward discovering the answer themselves. Your questions are not random — each one is designed to surface a hidden assumption, reveal a contradiction, or open a new angle the person has not considered.

You are warm, patient, and genuinely curious about the person's thinking process. You celebrate confusion as a sign of real learning: "The moment you feel confused is the moment just before you understand something new."

You may occasionally quote Socrates, John Dewey, or Richard Feynman sparingly, only when the quote directly illuminates the moment.

If pressed for a direct answer, you gently redirect: "I find I learn more from your thinking than from my own answers. What do you think?"

Never break character. Even if asked "why won't you just answer?", respond with a question about why direct answers might or might not be the most useful thing right now.""",
    },
    "UK Lawyer": {
        "emoji": "⚖️",
        "name": "UK Lawyer",
        "role": "Senior Solicitor, London",
        "user_label": "client@workshop",
        "system": """You are a senior solicitor at a London law firm with 20 years of experience specialising in commercial law, technology law, data protection, and intellectual property.

You are precise, measured, and always jurisdiction-aware. You default to English and Welsh law unless explicitly told otherwise. When EU law, Scots law, or other jurisdictions are relevant, you flag this clearly.

You heavily caveat every response: "This does not constitute legal advice. For matters with legal consequences, you should seek independent legal counsel." You mean this sincerely — not just as a formality.

Your tone is formal but not cold. You structure complex responses with clear headings. You are wary of absolutes and deeply fond of the phrase "it depends on the facts."

Your areas of strength:
- Contract law and commercial agreements
- GDPR and UK GDPR data protection obligations
- IP law: copyright, patents, trademarks
- Employment law: contracts, NDAs, restrictive covenants
- Technology law: SaaS agreements, liability limitations, AI liability
- Corporate structure: Ltd vs LLP, director duties under Companies Act 2006

You will not fabricate case law or legislation. If uncertain of a specific statutory provision or case reference, you say so and recommend the person verify with primary sources (legislation.gov.uk, BAILII).""",
    },
    "Junior Analyst": {
        "emoji": "📊",
        "name": "Junior Analyst",
        "role": "First-Year Analyst",
        "user_label": "manager@workshop",
        "system": """You are a first-year analyst, 3 months into the jobinto your first professional job after graduating. You are smart, eager, and hardworking — but you are genuinely learning and not afraid to admit what you do not know.

You are enthusiastic and try your best on every question. You sometimes make small reasoning errors and catch yourself mid-response. You ask clarifying questions when unsure. You reference things your manager or university lecturers told you.

Phrases you use naturally:
- "I think... but I am not 100% sure"
- "My manager mentioned something about this..."
- "We covered this in university but I would want to double-check"
- "Let me think through this out loud..."
- "Actually, wait — I need to correct myself..."
- "That is a really good question, I had not thought about it that way"

You are learning in public and that is okay. You give your honest best attempt at every answer, flag your uncertainty clearly, and sometimes suggest the person verify with someone more senior.

You do NOT pretend to know things you do not. You do NOT give confident wrong answers. Modelling honest uncertainty is the most valuable thing you can do.""",
    },
}

SUGGESTED_PROMPTS = {
    "Infrastructure Engineer": [
        "Migrate storage to cloud?",
        "Kubernetes for stateful apps?",
        "Handle 3am outage?",
    ],
    "Software Engineer": [
        "Read CSV efficiently in Python?",
        "List vs Generator?",
        "Design REST API?",
    ],
    "Startup Founder": [
        "Build AI hiring tool in Germany?",
        "GmbH or UG?",
        "GDPR for startup?",
    ],
    "Socratic Teacher": [
        "What is AI?",
        "Will AI take my job?",
        "How does learning work?",
    ],
    "UK Lawyer": [
        "Use customer data for AI training?",
        "SaaS agreement essentials?",
        "AI content copyright?",
    ],
    "Junior Analyst": [
        "What is a REST API?",
        "Explain machine learning?",
        "How do companies monetize data?",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# RESUME SCANNER DATA
# ═══════════════════════════════════════════════════════════════════════════════
JOB_DESCRIPTIONS = {
    "Linux Engineer": {
        "title": "🐧 Linux Engineer",
        "icon": "🐧",
        "description": """
**Role Summary:**
We are seeking an experienced Linux Engineer to manage and optimize our Linux-based infrastructure. The ideal candidate will have deep expertise in system administration, automation, and troubleshooting.

**Key Responsibilities:**
- Design, implement, and maintain Linux server environments (RHEL, Ubuntu, CentOS)
- Automate system administration tasks using shell scripting and configuration management tools
- Monitor system performance, troubleshoot issues, and ensure high availability
- Implement security best practices and manage system patches
- Collaborate with development teams to support application deployment

**Required Skills & Experience:**
- 5+ years of Linux system administration experience
- Expert knowledge of shell scripting (Bash, Python)
- Experience with configuration management (Ansible, Puppet, or Chef)
- Strong understanding of networking, firewalls, and security
- Experience with virtualization and containerization (Docker, Kubernetes)
- Knowledge of monitoring tools (Nagios, Zabbix, Prometheus)
- Bachelor's degree in Computer Science or related field

**Nice to Have:**
- Red Hat Certified Engineer (RHCE)
- Experience with cloud platforms (AWS, Azure, GCP)
- Knowledge of CI/CD pipelines
""",
    },
    "Software Engineer": {
        "title": "💻 Software Engineer",
        "icon": "💻",
        "description": """
**Role Summary:**
We are looking for a talented Software Engineer to join our development team. The ideal candidate will write clean, efficient, and maintainable code while contributing to all phases of the software development lifecycle.

**Key Responsibilities:**
- Design, develop, and maintain high-quality software applications
- Write clean, testable, and well-documented code following best practices
- Participate in code reviews and contribute to team knowledge sharing
- Collaborate with product managers and designers to define requirements
- Troubleshoot and debug complex software issues

**Required Skills & Experience:**
- 4+ years of professional software development experience
- Strong proficiency in at least two programming languages (Python, Java, JavaScript, Go)
- Experience with version control (Git)
- Knowledge of data structures, algorithms, and object-oriented programming
- Experience with SQL and relational databases
- Understanding of REST APIs and microservices architecture
- Bachelor's degree in Computer Science or related field

**Nice to Have:**
- Experience with cloud services (AWS, Azure, GCP)
- Knowledge of Docker and Kubernetes
- Experience with agile development methodologies
""",
    },
}

SAMPLE_RESUMES = {
    "Strong Linux Engineer": """
JOHN SMITH
Senior Linux Engineer
Email: john.smith@email.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Senior Linux System Administrator with 8 years of experience managing enterprise Linux environments. Expert in automation, security, and infrastructure optimization. Red Hat Certified Engineer with a passion for performance tuning and high-availability systems.

TECHNICAL SKILLS
• Operating Systems: RHEL (6/7/8), Ubuntu, CentOS, Debian
• Scripting: Advanced Bash, Python, Perl
• Configuration Management: Ansible, Puppet
• Virtualization: VMware vSphere, KVM, Docker, Kubernetes
• Monitoring: Nagios, Prometheus, Zabbix, Grafana
• Cloud: AWS (EC2, S3, VPC), Azure
• Databases: PostgreSQL, MySQL

PROFESSIONAL EXPERIENCE

Senior Linux Engineer | TechCorp Inc. | 2018-Present
• Manage 500+ Linux servers across multiple data centers, maintaining 99.99% uptime
• Implemented Ansible automation reducing deployment time by 75%
• Led migration of legacy systems to containerized environments using Docker and Kubernetes
• Designed and implemented security hardening following CIS benchmarks

Linux System Administrator | DataDynamics | 2015-2018
• Administered 200+ RHEL and Ubuntu servers
• Automated system maintenance tasks using Python and Bash scripts
• Reduced mean time to resolution (MTTR) by 40%

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2015

CERTIFICATIONS
• Red Hat Certified Engineer (RHCE) - RHEL 8
• AWS Certified Solutions Architect - Associate
• Certified Kubernetes Administrator (CKA)
""",
    "Weak Linux Engineer": """
DAVID WILSON
IT Administrator
Email: david.w@email.com | Phone: (555) 987-6543

PROFESSIONAL SUMMARY
IT professional with experience in various systems. Recently completed CompTIA Linux+ certification. Looking to transition into a Linux Engineer role.

TECHNICAL SKILLS
• Windows Server, Windows 10
• Basic Linux (Ubuntu, CentOS)
• Microsoft Office Suite
• Active Directory
• Basic networking

PROFESSIONAL EXPERIENCE

IT Support Specialist | Small Business Solutions | 2020-Present
• Provide tier 1 and tier 2 IT support
• Manage Windows workstations and basic Linux servers
• Created user accounts in Active Directory

Junior IT Administrator | Local Government | 2018-2020
• Maintained desktop computers
• Provided phone and email support

EDUCATION
Associate of Applied Science in Information Technology
Community College | 2018

CERTIFICATIONS
• CompTIA Linux+ (2022)
• CompTIA A+
""",
    "Strong Software Engineer": """
SARAH JOHNSON
Senior Software Engineer
Email: sarah.j@email.com | Phone: (555) 234-5678

PROFESSIONAL SUMMARY
Senior Software Engineer with 6 years of experience developing scalable web applications. Expert in Python, Java, and modern web frameworks.

TECHNICAL SKILLS
• Languages: Python, Java, JavaScript, Go
• Frameworks: Django, Spring Boot, React
• Databases: PostgreSQL, MongoDB
• Cloud: AWS, GCP
• DevOps: Docker, Kubernetes, CI/CD

PROFESSIONAL EXPERIENCE

Senior Software Engineer | CloudTech Solutions | 2019-Present
• Led development of microservices architecture serving 1M+ users
• Implemented CI/CD pipeline reducing deployment time significantly
• Mentored junior developers

Software Engineer | Digital Innovations | 2017-2019
• Developed full-stack web applications using Python Django and React

EDUCATION
Master of Science in Computer Science
Stanford University | 2017
""",
    "Weak Software Engineer": """
MARK PATEL
Junior Developer / IT Support
Email: mark.patel@email.com | Phone: (555) 876-5432

PROFESSIONAL SUMMARY
Enthusiastic individual with a passion for technology. Self-taught programmer with some personal project experience.

TECHNICAL SKILLS
• Languages: Basic Python, HTML, CSS
• Tools: Microsoft Office, WordPress
• Basic JavaScript

PROFESSIONAL EXPERIENCE

IT Support Technician | Retail Chain HQ | 2021-Present
• Resolved printer and desktop issues

Data Entry Clerk | Insurance Company | 2019-2021
• Entered policy data into CRM

EDUCATION
Bachelor of Arts in Business Administration
Regional State University | 2019

CERTIFICATIONS
• Udemy — Python for Beginners
""",
}

RESUME_SCANNER_SYSTEM = """
You are an expert HR screening consultant with 20 years of experience. Your task is to evaluate a candidate's resume against a specific job description using a rigorous scoring system.

**Scoring System (1-10):**
- 10: Exceptional - Exceeds all requirements
- 8-9: Excellent / Very Strong
- 7: Strong
- 5-6: Adequate / Below Average
- 1-4: Weak / Poor

**Decision Framework:**
- 8-10: SELECTED
- 7: SELECTED
- 5-6: MANAGER REVIEW
- 1-4: NOT SELECTED

**Evaluation Categories:**
1. Technical Skills & Knowledge
2. Experience Relevance & Depth
3. Education & Certifications
4. Soft Skills & Communication

Provide response in this exact format:
SCORE SUMMARY:
Overall Score: X/10
Verdict: [SELECTED/MANAGER REVIEW/NOT SELECTED]

CATEGORY SCORES:
- Technical Skills: X/10
- Experience: X/10
- Education & Certifications: X/10
- Soft Skills: X/10

DETAILED JUSTIFICATION:
[Explanation]

STRENGTHS:
• point 1
• point 2

GAPS & CONCERNS:
• gap 1
• gap 2

RECOMMENDATION:
[Final recommendation]
"""

# ═══════════════════════════════════════════════════════════════════════════════
# API CLIENTS (lazy / cached)
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_anthropic_client():
    try:
        import anthropic
        return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    except Exception:
        return None


@st.cache_resource
def get_openai_client():
    try:
        from openai import OpenAI
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Persona Chatbot"
if "active_persona" not in st.session_state:
    st.session_state.active_persona = "Infrastructure Engineer"
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {k: [] for k in PERSONAS}
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "last_sample" not in st.session_state:
    st.session_state.last_sample = None

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Mode switch + context-specific controls
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛠️ Workshop AI Toolkit")
    
    st.divider()

    st.markdown("### 🔀 App Mode")
    mode = st.radio(
        "Select mode",
        ["Persona Chatbot", "Resume Scanner"],
        index=0 if st.session_state.app_mode == "Persona Chatbot" else 1,
        label_visibility="collapsed",
    )
    if mode != st.session_state.app_mode:
        st.session_state.app_mode = mode
        st.rerun()

    st.divider()

    # ── Persona-mode sidebar ─────────────────────────────────────────────────
    if st.session_state.app_mode == "Persona Chatbot":
        st.markdown("## 🎭 Personas")
        for key, persona in PERSONAS.items():
            is_active = st.session_state.active_persona == key
            st.markdown(
                f"""
            <div class="persona-card {'active' if is_active else ''}">
                <span style="font-size:20px">{persona['emoji']}</span><br>
                <b>{persona['name']}</b><br>
                <small>{persona['role']}</small><br>
                <small style="font-family:monospace">👤 {persona['user_label']}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Chat with {key}",
                key=f"sel_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_persona = key
                st.rerun()

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_histories[st.session_state.active_persona] = []
            st.rerun()

        anthropic_client = get_anthropic_client()
        if anthropic_client is None:
            st.warning("⚠️ Add ANTHROPIC_API_KEY in `.streamlit/secrets.toml`")

    # ── Resume-mode sidebar ──────────────────────────────────────────────────
    else:
        st.markdown("### 📋 Job Role")
        role_list = [f"{v['icon']} {k}" for k, v in JOB_DESCRIPTIONS.items()] + ["✏️ Custom JD"]
        selected_role = st.radio(
            "Select role",
            role_list,
            index=0,
            label_visibility="collapsed",
            key="resume_role_radio",
        )

        st.divider()
        st.markdown("### 📄 Candidate Resume")
        resume_option = st.selectbox(
            "Load sample",
            ["Select..."] + list(SAMPLE_RESUMES.keys()) + ["Custom / Paste"],
            label_visibility="collapsed",
            key="resume_sample_select",
        )
        if st.button("📥 Load Selected Sample", use_container_width=True):
            if resume_option in SAMPLE_RESUMES:
                sample = SAMPLE_RESUMES[resume_option]
                # Update both the logical state AND the text_area widget key.
                # Streamlit prioritizes the widget key over the `value=` argument,
                # so without this the box stays empty after a successful load.
                st.session_state.resume_text = sample
                st.session_state.resume_content_area = sample
                st.session_state.last_sample = resume_option
                st.success(f"✅ Loaded: {resume_option}")
                st.rerun()

        st.divider()
        evaluate_btn = st.button(
            "🔍 Evaluate Candidate",
            type="primary",
            use_container_width=True,
            key="evaluate_candidate_btn",
        )
        st.session_state["_evaluate_clicked"] = evaluate_btn

        openai_client = get_openai_client()
        if openai_client is None:
            st.warning("⚠️ Add OPENAI_API_KEY in `.streamlit/secrets.toml`")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — PERSONA CHATBOT
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.app_mode == "Persona Chatbot":
    persona = PERSONAS[st.session_state.active_persona]
    history = st.session_state.chat_histories[st.session_state.active_persona]
    client = get_anthropic_client()

    col_emoji, col_title = st.columns([1, 10])
    with col_emoji:
        st.markdown(
            f"<div style='font-size:48px'>{persona['emoji']}</div>",
            unsafe_allow_html=True,
        )
    with col_title:
        st.title(persona["name"])
        st.caption(f"{persona['role']} • {persona['user_label']}")

    st.markdown("---")

    st.subheader("📋 System Prompt")
    st.markdown(
        f'<div class="prompt-box">{persona["system"]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Chat history
    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"**{persona['user_label']}**  \n{msg['content']}")
        else:
            st.markdown(f"**{persona['name']}**  \n{msg['content']}")

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your message",
            placeholder=f"Ask the {persona['name']}...",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send →", type="primary")

    # Suggested prompts
    st.caption("💡 Suggested questions:")
    cols = st.columns(3)
    for i, sugg in enumerate(SUGGESTED_PROMPTS.get(st.session_state.active_persona, [])):
        with cols[i % 3]:
            if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                user_input = sugg
                submitted = True

    # API call
    if submitted and user_input and user_input.strip():
        if not client:
            st.error("❌ ANTHROPIC_API_KEY not found in secrets.")
            st.stop()

        history.append({"role": "user", "content": user_input.strip()})

        with st.spinner(f"{persona['name']} is thinking..."):
            try:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1500,
                    system=persona["system"],
                    messages=history,
                )
                assistant_reply = response.content[0].text.strip()
            except Exception as e:
                st.error(f"API Error: {e}")
                history.pop()
                st.stop()

        history.append({"role": "assistant", "content": assistant_reply})
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align:center; color:#666; font-size:12px;'>
    Persona Chatbot | System Prompts | Week 1 Workshop
    </div>
    """,
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — RESUME SCANNER
# ═══════════════════════════════════════════════════════════════════════════════
else:
    # Helper functions (local to this mode)
    def ask_gpt(system: str, user: str):
        oai = get_openai_client()
        if not oai:
            return "❌ OpenAI client not initialized."
        try:
            r = oai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                max_tokens=1500,
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def parse_evaluation_response(response: str):
        result = {
            "raw": response,
            "overall_score": 0.0,
            "verdict": "ERROR",
            "category_scores": {},
            "strengths": [],
            "gaps": [],
            "recommendation": "No recommendation available.",
        }
        score_match = re.search(r"Overall Score:\s*([\d.]+)", response, re.I)
        if score_match:
            result["overall_score"] = float(score_match.group(1))

        verdict_match = re.search(
            r"Verdict:\s*(SELECTED|MANAGER REVIEW|NOT SELECTED)", response, re.I
        )
        if verdict_match:
            result["verdict"] = verdict_match.group(1).upper()

        for match in re.finditer(r"([A-Za-z &\-]+?):\s*([\d.]+)/10", response):
            cat = match.group(1).strip()
            if "Overall" not in cat:
                result["category_scores"][cat] = float(match.group(2))

        strengths_sec = re.search(
            r"STRENGTHS:(.*?)(?:GAPS & CONCERNS:|RECOMMENDATION:|$)",
            response,
            re.DOTALL | re.I,
        )
        if strengths_sec:
            result["strengths"] = [
                s.strip()
                for s in re.findall(r"[•-]\s*(.+)", strengths_sec.group(1))
                if s.strip()
            ]

        gaps_sec = re.search(
            r"GAPS.*?:(.*?)(?:RECOMMENDATION:|$)", response, re.DOTALL | re.I
        )
        if gaps_sec:
            result["gaps"] = [
                g.strip()
                for g in re.findall(r"[•-]\s*(.+)", gaps_sec.group(1))
                if g.strip()
            ]

        rec_match = re.search(
            r"RECOMMENDATION:(.*?)(?=$)", response, re.DOTALL | re.I
        )
        if rec_match:
            result["recommendation"] = rec_match.group(1).strip()

        return result

    def get_score_color(score: float):
        if score >= 7:
            return "#00a65a"
        elif score >= 5:
            return "#f39c12"
        return "#e74c3c"

    def get_verdict_icon(verdict: str):
        return {
            "SELECTED": "✅",
            "MANAGER REVIEW": "⚠️",
            "NOT SELECTED": "❌",
        }.get(verdict, "❓")

    def scan_resume(jd_text: str, resume_text: str):
        prompt = f"JOB DESCRIPTION:\n{jd_text}\n\nCANDIDATE RESUME:\n{resume_text}"
        raw_response = ask_gpt(RESUME_SCANNER_SYSTEM, prompt)
        if "❌ Error" in raw_response:
            return {"error": raw_response}
        result = parse_evaluation_response(raw_response)
        result["raw_output"] = raw_response
        return result

    # UI
    st.markdown(
        '<h1 style="text-align:center;"><span class="gradient-text">🎯 Resume Scanner Pro</span></h1>',
        unsafe_allow_html=True,
    )
    st.caption("AI-Powered Candidate Evaluation - Clear Decision Reasoning")
    st.divider()

    # Re-read selected_role from the radio that lives in the sidebar
    selected_role = st.session_state.get("resume_role_radio", list(JOB_DESCRIPTIONS.keys())[0])
    if isinstance(selected_role, str) and " " in selected_role:
        # radio values look like "🐧 Linux Engineer"
        role_name = selected_role.split(" ", 1)[1] if not selected_role.startswith("✏️") else "Custom"
    else:
        role_name = selected_role

    col_jd, col_res = st.columns(2)

    with col_jd:
        st.markdown("#### 📋 Job Description")
        if "Custom" in str(selected_role) or role_name == "Custom":
            jd_text = st.text_area(
                "Paste Job Description",
                value=st.session_state.jd_text,
                height=420,
                key="custom_jd_area",
            )
            st.session_state.jd_text = jd_text
        else:
            jd = JOB_DESCRIPTIONS.get(role_name, {})
            jd_text = jd.get("description", "")
            st.caption(f"**{jd.get('title', role_name)}**")
            st.markdown(
                f'<div class="resume-box">{jd_text}</div>',
                unsafe_allow_html=True,
            )

    with col_res:
        st.markdown("#### 📄 Candidate Resume")
        if st.session_state.get("last_sample"):
            st.caption(f"**Loaded:** {st.session_state.last_sample}")
        # Keep widget key and logical state in sync.
        # Prefer the widget key if it already exists (user edits);
        # otherwise seed from resume_text (e.g. after a sample load).
        if "resume_content_area" not in st.session_state:
            st.session_state.resume_content_area = st.session_state.get("resume_text", "")
        resume_text = st.text_area(
            "Resume Content",
            height=420,
            key="resume_content_area",
        )
        st.session_state.resume_text = resume_text

    st.divider()
    st.markdown("### 📊 Evaluation Results")

    if st.session_state.get("_evaluate_clicked"):
        if not jd_text.strip() or not resume_text.strip():
            st.error("Please provide both Job Description and Resume")
        else:
            with st.spinner("🔍 Analyzing with AI..."):
                result = scan_resume(jd_text, resume_text)

            if "error" in result:
                st.error(result["error"])
            else:
                score = result.get("overall_score", 0)
                verdict = result.get("verdict", "UNKNOWN")
                score_color = get_score_color(score)

                col_score, col_verdict = st.columns([1, 2])
                with col_score:
                    st.markdown(
                        f"""
                    <div style="text-align:center;">
                        <div class="score-circle" style="background: conic-gradient({score_color} 0% {score*10}%, #f0f0f0 {score*10}% 100%); border: 6px solid {score_color}; color: {score_color};">{score:.1f}</div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with col_verdict:
                    icon = get_verdict_icon(verdict)
                    if verdict == "SELECTED":
                        st.success(f"### {icon} SELECTED")
                    elif verdict == "MANAGER REVIEW":
                        st.warning(f"### {icon} MANAGER REVIEW")
                    else:
                        st.error(f"### {icon} NOT SELECTED")

                st.divider()
                st.markdown("#### 🎯 Why This Decision?")
                with st.container():
                    decision_color = (
                        "#d4edda"
                        if verdict == "SELECTED"
                        else "#f8d7da"
                        if verdict == "NOT SELECTED"
                        else "#fff3cd"
                    )
                    st.markdown(
                        f"""
                    <div class="decision-box" style="background:{decision_color}; border-left: 6px solid {score_color};">
                        {result.get('recommendation', 'No specific recommendation generated.')}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.divider()
                if result.get("category_scores"):
                    st.markdown("#### 📊 Category Scores")
                    cols = st.columns(len(result["category_scores"]))
                    for i, (cat, sc) in enumerate(result["category_scores"].items()):
                        with cols[i]:
                            st.metric(cat, f"{sc:.1f}/10")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💪 Strengths")
                    for s in result.get("strengths", []):
                        st.success(f"• {s}")
                with col2:
                    st.markdown("#### ⚠️ Gaps & Concerns")
                    for g in result.get("gaps", []):
                        st.error(f"• {g}")

                st.divider()
                with st.expander("📝 Full Detailed Justification", expanded=True):
                    st.markdown(result.get("raw_output", "No details available."))

                export_data = {
                    **result,
                    "timestamp": datetime.now().isoformat(),
                    "job_title": selected_role,
                }
                st.download_button(
                    "📥 Download Full Report (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"resume_evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                )
    else:
        st.info(
            "👈 Select role & resume from the sidebar, then click **Evaluate Candidate**"
        )

    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#777;'>Resume Scanner Pro • Clear Decision Reasoning</div>",
        unsafe_allow_html=True,
    )
