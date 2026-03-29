# 🧠 DS Interview Coach — Full Technical Explanation

> This document explains the architecture, code design, and key concepts behind the DS Interview Coach app.
> Use this to confidently explain the project in interviews or to onboard collaborators.

---

## The Big Picture

You built a **multi-agent AI application** with two distinct AI personas working together — an **Interviewer** and an **Evaluator** — orchestrated through a Streamlit web interface.

The key architectural insight is that **one LLM plays two different roles** depending on what prompt you give it. This is a fundamental pattern in production GenAI systems at companies like American Express, Google, and OpenAI itself.

```
User
 │
 ▼
Streamlit UI (app.py)
 │
 ├──► Interviewer Agent  ──► GPT-4.1-nano ──► Generates next question
 │
 ├──► Evaluator Agent   ──► GPT-4.1-nano ──► Scores and critiques answer
 │
 └──► Report Generator  ──► GPT-4.1-nano ──► Final performance summary
```

---

## The 3 Files and What Each Does

### 1. `config.py` — The Brain's Instructions

This file contains nothing but text — no logic, no code execution.
But it is the **most important file** because it defines how the AI behaves.

It has three prompts:

#### INTERVIEWER_PROMPT
Tells GPT to act as a senior BFSI interviewer. Key design decisions:

- *"Ask ONE question at a time. Never ask multiple questions together."*
  This is **prompt engineering** — constraining the model's behavior through careful instruction.
- Dynamically injects variables like `{domain}`, `{difficulty}`, `{question_num}` at runtime.
  The same prompt works for any combination of settings the user picks.

#### EVALUATOR_PROMPT
Switches the model into a completely different persona — a strict evaluator.

- Asks for output in a **structured format**: SCORE, STRENGTHS, GAPS, VERDICT.
- Structured output makes responses easy to parse and display consistently in the UI.
- This pattern is called **output formatting via prompt** — a core GenAI technique.

#### FINAL_REPORT_PROMPT
Takes the entire interview transcript and generates a holistic performance summary.

- Receives the full context of everything that happened — all questions, all answers, all evaluations.
- Synthesizes it into actionable feedback: strengths, gaps, next steps.

**Why a separate config file?**
Separation of concerns — if you want to change how the AI behaves, you only touch `config.py`.
The logic and UI don't need to change at all. This is standard software engineering practice.

---

### 2. `interviewer.py` — The API Layer

Three functions, each making one call to the OpenAI API.

#### `get_next_question()`

```python
def get_next_question(domain, difficulty, question_num, total_questions, conversation_history):
```

The most architecturally interesting function. It takes `conversation_history` as a parameter —
a list of every message exchanged so far:

```python
[
  {"role": "assistant", "content": "What is the bias-variance tradeoff?"},
  {"role": "user", "content": "Bias is the error from wrong assumptions..."},
  {"role": "assistant", "content": "Good. Now explain overfitting."},
  ...
]
```

By passing the full history on every call, you give the model **memory** of the entire interview.
GPT has no memory by default — it is stateless. Passing history explicitly is how you simulate
a continuous conversation. This pattern is called **context window management** and is used
in every production chatbot ever built.

#### `evaluate_answer()`

```python
def evaluate_answer(question, answer, domain, difficulty):
```

Intentionally **stateless** — only receives the current question and answer, nothing else.

This is a deliberate design choice:
- The evaluator doesn't need to know what came before — it judges this one answer fairly.
- Keeping it stateless makes it cheaper (fewer tokens) and more consistent.
- Same input always produces comparable output — important for fairness across candidates.

#### `generate_final_report()`

```python
def generate_final_report(domain, difficulty, total_questions, transcript):
```

Receives the full `transcript` — a single string containing all questions, answers,
and evaluations concatenated together. Passes this entire context to the model in one call.

This is an example of **RAG-lite** — injecting retrieved context (the transcript) into a
prompt to generate a grounded, evidence-based response.

---

### 3. `app.py` — The UI and State Machine

The most complex file. Two big concepts to understand here.

#### Concept 1: Session State

Streamlit has an unusual behavior — it **reruns the entire Python script from top to bottom
on every single user interaction**:

- Click a button? Full rerun.
- Type in a text box? Full rerun.
- Select a dropdown? Full rerun.

This means normal Python variables get wiped on every interaction.

`st.session_state` is a special dictionary that **persists across reruns**.
Every important variable lives here:

```python
st.session_state.started            # Has the interview begun?
st.session_state.question_num       # Which question are we on?
st.session_state.conversation_history  # Full message history for GPT
st.session_state.current_question   # The question currently on screen
st.session_state.evaluations        # List of all evaluation responses
st.session_state.transcript         # Full running log of the interview
st.session_state.interview_done     # Has the interview finished?
st.session_state.final_report       # The generated final report text
```

This is equivalent to managing application state in React, Angular, or any frontend framework.

#### Concept 2: The Three-Screen State Machine

The app is essentially a **state machine** with three states:

```
State 1: Welcome Screen
  started = False
  → User configures settings, clicks Start
  → Transitions to State 2

State 2: Active Interview
  started = True, interview_done = False
  → Shows current question
  → User types answer, clicks Submit
  → Evaluation displayed
  → Click Next Question → stays in State 2 (question_num increments)
  → After last question → transitions to State 3

State 3: Results Screen
  interview_done = True
  → Final report generated and displayed
  → Full transcript shown in expander
```

Each state is a different `if/elif/else` branch in the code.
Transitions happen by updating session state variables and calling `st.rerun()`.

#### The Submit Answer Flow (Step by Step)

1. User types answer and clicks Submit
2. App calls `evaluate_answer()` → structured feedback from GPT
3. Feedback appended to `st.session_state.transcript`
4. Feedback displayed on screen
5. If more questions remain → "Next Question" button appears
6. Clicking Next Question:
   - Increments `question_num`
   - Calls `get_next_question()` with updated history
   - Stores new question in session state
   - Calls `st.rerun()` to refresh UI
7. If last question → "View Final Report" button appears instead

---

## Key Technical Concepts for Interviews

### 1. Dual-Agent Architecture
Same underlying LLM, two distinct personas defined by different system prompts.
In production systems, you would have many more specialized agents — one per task type.

**Interview talking point:**
*"I used a dual-agent pattern where the same GPT-4.1-nano model plays two roles —
an interviewer that maintains conversational context, and a stateless evaluator that
scores each answer independently for consistency."*

---

### 2. Prompt Engineering
Controlling model behavior entirely through text instructions — no fine-tuning, no training.
Key techniques used in this project:
- **Persona assignment** ("You are a senior BFSI interviewer")
- **Behavioral constraints** ("Ask ONE question at a time")
- **Variable injection** (`{domain}`, `{difficulty}`, `{question_num}`)
- **Output format enforcement** (SCORE: X/10, VERDICT: Pass/Fail)

---

### 3. Context Window Management
Passing conversation history explicitly on every API call to simulate memory.
GPT is stateless — it remembers nothing between calls.
The history list grows with each turn and is sent in full each time.

**Trade-off to mention:** Longer history = more tokens = higher cost.
In production you would implement summarization or sliding window truncation
to manage context length at scale.

---

### 4. Structured Output
Instructing the model to return data in a predictable format so the application
can reliably parse and display it. In this project done via prompt instruction.

**Production upgrade:** Use OpenAI's JSON mode or Pydantic models for guaranteed
structured output — worth mentioning as a known improvement area.

---

### 5. Stateful UI on a Stateless Framework
Using Streamlit's `session_state` to build a multi-step application on top of a
framework that reruns everything on every interaction.

Analogous to:
- `useState` in React
- Session variables in Flask
- Redux store in large frontend apps

---

### 6. Separation of Concerns
- `config.py` — prompt definitions (what the AI does)
- `interviewer.py` — API calls (how we talk to the AI)
- `app.py` — UI and state (what the user sees)

Each layer has one job. This makes the system easy to maintain, test, and extend.
Adding a new agent means adding a prompt to `config.py` and a function to `interviewer.py`
— the UI layer doesn't need to change.

---

## How to Frame It in an Interview

**30-second elevator pitch:**

> "I built a multi-agent interview coaching system where a single LLM plays two distinct
> roles — an interviewer and an evaluator — controlled entirely through prompt engineering.
> The interviewer maintains conversational context by passing full message history on every
> API call, while the evaluator is intentionally stateless for consistency and cost efficiency.
> The UI is built in Streamlit with explicit session state management to handle the multi-step
> interview flow across question generation, answer evaluation, and final report generation."

**Follow-up questions you should be ready for:**

| Question | Key Point to Make |
|---|---|
| How does the model remember previous questions? | Full conversation history passed on every API call — GPT is stateless by design |
| Why is the evaluator stateless? | Consistency and cost — it only needs current Q&A to judge fairly |
| How would you scale this? | Add JSON mode for structured output, sliding window for context, Redis for session persistence |
| How would you improve answer quality? | Fine-tune on domain-specific Q&A pairs, add retrieval from a question bank |
| What's the cost per session? | ~$0.001 per session with gpt-4.1-nano — 5000 sessions per $5 |
| How would you add more agents? | New prompt in config.py, new function in interviewer.py — UI unchanged |

---

## Possible Extensions (Good to Mention Proactively)

- **Voice interface** — use OpenAI Whisper for speech-to-text input
- **PDF report export** — generate a downloadable session report using ReportLab
- **Question bank RAG** — embed a curated question database and retrieve relevant questions
- **Difficulty adaptation** — auto-adjust difficulty based on running score
- **Multi-user support** — add authentication and store sessions in a database
- **JSON structured output** — replace prompt-based formatting with Pydantic models

---

*Built by Sajal Jain — Sr. Manager Data Science, American Express*
*Stack: Python · OpenAI GPT-4.1-nano · Streamlit · Dual-Agent Architecture*
