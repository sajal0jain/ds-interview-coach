# interviewer.py

from openai import OpenAI
from config import MODEL, INTERVIEWER_PROMPT, EVALUATOR_PROMPT, FINAL_REPORT_PROMPT

client = OpenAI()


def get_next_question(domain, difficulty, question_num, total_questions, conversation_history):
    """Ask the interviewer agent to generate the next question."""

    system_prompt = INTERVIEWER_PROMPT.format(
        domain=domain,
        difficulty=difficulty,
        question_num=question_num,
        total_questions=total_questions,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *conversation_history,
        ],
    )

    return response.choices[0].message.content


def evaluate_answer(question, answer, domain, difficulty):
    """Ask the evaluator agent to score and critique the answer."""

    system_prompt = EVALUATOR_PROMPT.format(
        question=question,
        answer=answer,
        domain=domain,
        difficulty=difficulty,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Please evaluate this answer now."},
        ],
    )

    return response.choices[0].message.content


def generate_final_report(domain, difficulty, total_questions, transcript):
    """Generate the overall performance report at the end."""

    system_prompt = FINAL_REPORT_PROMPT.format(
        domain=domain,
        difficulty=difficulty,
        total_questions=total_questions,
        transcript=transcript,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the final report now."},
        ],
    )

    return response.choices[0].message.content
