# app.py
import os
import streamlit as st
import tempfile
import subprocess
from groq import Groq
from pathlib import Path

# Set page config
st.set_page_config(page_title="AutoTest Agent", layout="wide")

# Groq API client
client = Groq(api_key="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")

st.title("🤖 AutoTest Agent - AI Powered Test Case Generator")

# --- Sidebar ---
framework = st.sidebar.radio("Select Test Framework", ("unittest", "pytest"))
execute_tests = st.sidebar.checkbox("Execute Tests after Generation", value=True)

# --- Upload code or paste ---
st.subheader("1. Upload or Paste Python Code")
uploaded_file = st.file_uploader("Upload a Python file", type=[".py"])
code_input = st.text_area("Or paste Python code here", height=200)

st.subheader("2. Describe the Use Case")
description = st.text_area("Describe what the code is supposed to do", height=150)

generate_button = st.button("🚀 Generate Test Cases")

# --- Main processing ---
def extract_code():
    if uploaded_file:
        return uploaded_file.read().decode("utf-8")
    return code_input

def generate_test_cases(code, desc, framework):
    prompt = f"""
You are a helpful AI agent. Based on the provided code and use-case description,
write comprehensive test cases using the {framework} framework.
Include edge cases, boundary conditions, and provide high coverage.
Explain the logic behind the test cases as comments.

Code:
{code}

Use-case:
{desc}
"""
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content

def run_tests(code):
    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = Path(tmpdir) / "test_code.py"
        code_path.write_text(code)
        try:
            result = subprocess.run(
                ["pytest", str(code_path)] if "pytest" in code else ["python3", str(code_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout + "\n" + result.stderr
        except Exception as e:
            return str(e)

# --- Output Area ---
if generate_button:
    code = extract_code()
    if not code.strip() or not description.strip():
        st.error("Please provide both code and use-case description.")
    else:
        with st.spinner("Generating test cases using LLaMA 3 via Groq API..."):
            test_output = generate_test_cases(code, description, framework)
        st.success("Test Cases Generated")

        st.subheader("📄 Generated Test Cases")
        st.code(test_output, language="python")

        st.download_button("💾 Save to File", test_output, file_name="generated_tests.py")
        st.button("📋 Copy to Clipboard", on_click=lambda: st.toast("Copied!"))

        if execute_tests:
            st.subheader("⚙️ Test Execution Results")
            test_result = run_tests(test_output)
            st.text_area("Results", test_result, height=300)

        st.subheader("🔁 Feedback")
        feedback = st.radio("Was this helpful?", ["👍 Yes", "👎 No"])
        user_notes = st.text_input("Any suggestions to improve?")
