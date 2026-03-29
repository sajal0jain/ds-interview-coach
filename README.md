# 🎯 DS Interview Coach using GPT

An AI-powered Data Science Interview Coach built with GPT-4.1-nano and Streamlit.

## What it does
- Conducts mock Data Science interviews across 5 domains
- Evaluates your answers with scores, strengths, and gaps
- Generates a full performance report at the end of each session

## Domains Covered
- Statistics & Probability
- Machine Learning
- SQL & Data Manipulation
- Business Case Study
- Python & Coding

## Tech Stack
- **LLM:** OpenAI GPT-4.1-nano
- **UI:** Streamlit
- **Architecture:** Dual-agent (Interviewer + Evaluator)
- **Language:** Python

## How to Run

1. Clone the repo
   git clone https://github.com/sajal0jain/ds-interview-coach.git

2. Install dependencies
   pip install openai streamlit python-dotenv

3. Add your OpenAI API key — create a .env file
   OPENAI_API_KEY=sk-your-key-here

4. Run the app
   streamlit run app.py

## Architecture
The app uses a dual-agent design pattern:
- **Interviewer Agent** — generates domain-specific questions and maintains conversation context across the session
- **Evaluator Agent** — independently scores each answer on accuracy, depth, structure, and example quality
- **Report Generator** — synthesizes all evaluations into a final performance summary

## Author
Sajal Jain 
