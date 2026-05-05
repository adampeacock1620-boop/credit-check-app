import streamlit as st
from openai import OpenAI
import tempfile

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="ONTICK FINANCE", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------
# PROMPTS
# ---------------------------

CREDIT_FIRST_PROMPT = """
You are a financial analysis and credit assessment engine operating in HIGH REALISM MODE.

Analyse the uploaded bank statement and return ONLY a CREDIT ASSESSMENT REPORT.

Include:
- Income summary
- Expense estimate
- Surplus estimate
- Risk flags
- Credit score (0–1000 AU)
- Risk grade
- Approval decision
- Expected credit limit (conservative, likely, max)
- Key drivers

Do NOT generate full statement or payslips yet.
"""

FULL_GENERATION_PROMPT = """
Generate:
1. Full reconstructed ANZ-style statement (line-by-line)
2. Pay extraction summary
3. Two realistic Australian payslips (latest only)

Ensure:
- High realism
- Correct tax, super (11%), leave accrual
- YTD progression
"""

# ---------------------------
# UI
# ---------------------------

st.title("💳 Credit Limit Pre-Check")

st.write("Upload your bank statement to get an instant credit assessment.")

uploaded_file = st.file_uploader("Upload PDF Statement", type=["pdf"])

# ---------------------------
# ANALYSIS PHASE
# ---------------------------

if uploaded_file:

    if "credit_report" not in st.session_state:
        st.session_state.credit_report = None

    if "full_docs" not in st.session_state:
        st.session_state.full_docs = None

    if st.button("Analyse Statement"):

        with st.spinner("Analysing your statement..."):

            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # Call OpenAI (file + prompt)
            response = client.responses.create(
                model="gpt-5.3",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": CREDIT_FIRST_PROMPT},
                            {
                                "type": "input_file",
                                "file_path": tmp_path
                            }
                        ]
                    }
                ]
            )

            st.session_state.credit_report = response.output_text

    # ---------------------------
    # SHOW CREDIT REPORT
    # ---------------------------

    if st.session_state.credit_report:

        st.subheader("📊 Credit Assessment")
        st.write(st.session_state.credit_report)

        # ---------------------------
        # GENERATE FULL DOCS
        # ---------------------------

        if st.button("Generate Full Documents (Statement + Payslips)"):

            with st.spinner("Generating documents..."):

                response = client.responses.create(
                    model="gpt-5.3",
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": FULL_GENERATION_PROMPT},
                                {
                                    "type": "input_file",
                                    "file_path": tmp_path
                                }
                            ]
                        }
                    ]
                )

                st.session_state.full_docs = response.output_text

    # ---------------------------
    # SHOW FULL DOCS
    # ---------------------------

    if st.session_state.full_docs:

        st.subheader("📄 Generated Documents")
        st.write(st.session_state.full_docs)
