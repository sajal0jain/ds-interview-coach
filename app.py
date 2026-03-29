# app.py

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from interviewer import evaluate_answer, generate_final_report, get_next_question
from config import DIFFICULTY_LEVELS, DOMAINS

# ── Page Setup ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Data Science Interview Coach", layout="wide")

st.title("Data Science Interview Coach")
st.caption("Powered by GPT-4.1 nano | Built for BFSI & Analytics roles")

if not os.getenv("OPENAI_API_KEY"):
    st.error(
        "Missing `OPENAI_API_KEY`. Add it to your `.env` file in this folder "
        "or set the environment variable, then restart Streamlit."
    )
    st.stop()

# ── Session State Init ────────────────────────────────────────────────────────

if "started" not in st.session_state:
    st.session_state.started = False
if "question_num" not in st.session_state:
    st.session_state.question_num = 1
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "evaluations" not in st.session_state:
    st.session_state.evaluations = []
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "interview_done" not in st.session_state:
    st.session_state.interview_done = False
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "after_submit" not in st.session_state:
    st.session_state.after_submit = False
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None

# ── Sidebar: Interview Settings ───────────────────────────────────────────────

with st.sidebar:
    st.header("Interview Settings")

    domain = st.selectbox("Domain", DOMAINS)
    difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS)
    total_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)

    st.divider()

    if st.button("Start New Interview", use_container_width=True):
        st.session_state.started = False
        st.session_state.question_num = 1
        st.session_state.conversation_history = []
        st.session_state.current_question = None
        st.session_state.evaluations = []
        st.session_state.transcript = ""
        st.session_state.interview_done = False
        st.session_state.final_report = None
        st.session_state.after_submit = False
        st.session_state.last_evaluation = None
        st.rerun()

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. Choose your domain & difficulty")
    st.markdown("2. Answer each question in the text box")
    st.markdown("3. Get instant feedback after each answer")
    st.markdown("4. Receive a full report at the end")

# ── Main Area ─────────────────────────────────────────────────────────────────

if not st.session_state.started:
    st.markdown("### Welcome! Configure your interview in the sidebar and click below to begin.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Interview", use_container_width=True, type="primary"):
            st.session_state.started = True
            st.session_state.after_submit = False
            st.session_state.last_evaluation = None
            with st.spinner("Your interviewer is preparing the first question..."):
                question = get_next_question(
                    domain,
                    difficulty,
                    st.session_state.question_num,
                    total_questions,
                    st.session_state.conversation_history,
                )
                st.session_state.current_question = question
                st.session_state.conversation_history.append({"role": "assistant", "content": question})
            st.rerun()

elif st.session_state.interview_done:
    st.success("Interview complete!")

    if st.session_state.final_report is None:
        with st.spinner("Generating your performance report..."):
            st.session_state.final_report = generate_final_report(
                domain, difficulty, total_questions, st.session_state.transcript
            )

    st.markdown("## Your performance report")
    st.markdown(st.session_state.final_report)

    st.divider()
    st.markdown("### Full interview transcript")
    with st.expander("Click to view all questions and evaluations"):
        st.text(st.session_state.transcript)

else:
    progress = (st.session_state.question_num - 1) / total_questions
    st.caption(
        f"Question {st.session_state.question_num} of {total_questions} | {domain} | {difficulty}"
    )
    st.progress(progress)

    st.divider()

    if st.session_state.after_submit and st.session_state.last_evaluation is not None:
        st.markdown("### Feedback")
        st.markdown(st.session_state.last_evaluation)
        st.divider()

        if st.session_state.question_num >= total_questions:
            if st.button("View Final Report", type="primary"):
                st.session_state.interview_done = True
                st.session_state.after_submit = False
                st.session_state.last_evaluation = None
                st.rerun()
        else:
            if st.button("Next Question", type="primary"):
                st.session_state.after_submit = False
                st.session_state.last_evaluation = None
                st.session_state.question_num += 1
                with st.spinner("Preparing next question..."):
                    next_question = get_next_question(
                        domain,
                        difficulty,
                        st.session_state.question_num,
                        total_questions,
                        st.session_state.conversation_history,
                    )
                    st.session_state.current_question = next_question
                    st.session_state.conversation_history.append(
                        {"role": "assistant", "content": next_question}
                    )
                st.rerun()
    else:
        st.markdown(f"### Question {st.session_state.question_num}")
        st.info(st.session_state.current_question)

        with st.form(f"answer_form_{st.session_state.question_num}", clear_on_submit=False):
            answer = st.text_area(
                "Your answer",
                height=200,
                placeholder="Type your answer here. Take your time — think before you write.",
                key=f"answer_{st.session_state.question_num}",
            )
            submitted = st.form_submit_button("Submit answer", type="primary")

        if submitted:
            if not answer.strip():
                st.warning("Please enter an answer before submitting.")
            else:
                with st.spinner("Evaluating your answer..."):
                    evaluation = evaluate_answer(
                        st.session_state.current_question,
                        answer,
                        domain,
                        difficulty,
                    )

                st.session_state.transcript += f"""
Q{st.session_state.question_num}: {st.session_state.current_question}
Answer: {answer}
Evaluation: {evaluation}
---
"""
                st.session_state.evaluations.append(evaluation)
                st.session_state.conversation_history.append({"role": "user", "content": answer})
                st.session_state.last_evaluation = evaluation
                st.session_state.after_submit = True
                st.rerun()
