import streamlit as st
import random
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
open_api_key = os.getenv("OPENROUTER_API_KEY")
if not open_api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not configured")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=open_api_key,
)

themes = ["data analytics", "data science", "data engineering", "python", "statistics", "AI"]


def generate_puzzle(theme):
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {
                "role": "system",
                "content": "You write funny jokes and clever riddles. Return only valid JSON with exactly these string fields: joke, riddle, answer.",
            },
            {
                "role": "user",
                "content": f"Create a joke and a riddle about {theme}. The answer must solve the riddle.",
            },
        ],
        max_tokens=2000,
        extra_body={"reasoning": {"enabled": True}},
    )
    content = response.choices[0].message.content or ""
    content = content.removeprefix("```json").removesuffix("```").strip()
    return json.loads(content)


if "puzzle" not in st.session_state:
    st.session_state.theme = random.choice(themes)
    st.session_state.puzzle = generate_puzzle(st.session_state.theme)
    st.session_state.show_answer = False

st.title("Joke and Riddle")

refresh_clicked, answer_clicked = st.columns(2)
with refresh_clicked:
    if st.button("Refresh", use_container_width=True):
        other_themes = [theme for theme in themes if theme != st.session_state.theme]
        st.session_state.theme = random.choice(other_themes)
        st.session_state.puzzle = generate_puzzle(st.session_state.theme)
        st.session_state.show_answer = False
        st.rerun()

with answer_clicked:
    answer_label = "Hide answer" if st.session_state.show_answer else "Show answer"
    if st.button(answer_label, use_container_width=True):
        st.session_state.show_answer = not st.session_state.show_answer
        st.rerun()

st.subheader("Joke")
st.write(st.session_state.puzzle["joke"])
st.subheader("Riddle")
st.write(st.session_state.puzzle["riddle"])

if st.session_state.show_answer:
    st.success(f"Answer: {st.session_state.puzzle['answer']}")
