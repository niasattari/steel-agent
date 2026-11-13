import streamlit as st
from agent import agent

st.set_page_config(page_title="Steel Trade Analyst", layout="wide")
st.title("Steel Trade Analyst Agent")
st.caption("Germany's flat-rolled steel trade (HS 7208-7212) with 5 partners, "
           "UN Comtrade 2019-2024")

examples = [
    "How did Germany's flat-rolled steel imports from China change between 2021 and 2024, in tonnes and USD per tonne?",
    "Are there data inconsistencies for South Korea?",
    "Which partner had the highest average price per tonne in 2023?",
    "Compare Germany's imports from India and Türkiye over time.",
]
choice = st.selectbox("Example questions", [""] + examples)
question = st.text_input("Or ask your own question", value=choice)

if st.button("Ask") and question:
    with st.spinner("Analysing the data..."):
        text, trace, (tin, tout) = agent(question)
    st.markdown(text)
    st.divider()
    st.subheader("How the agent got there")
    for i, step in enumerate(trace, 1):
        with st.expander(f"Step {i}: {step['tool']}"):
            if step["tool"] == "run_sql":
                st.code(step["input"]["query"], language="sql")
            else:
                st.json(step["input"])
            st.text(step["output"])
    st.caption(f"Tokens: {tin:,} in / {tout:,} out "
               f"(about ${(tin * 2 + tout * 10) / 1e6:.3f} at $2/$10 per million)")
