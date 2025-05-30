import streamlit as st
import openai
from datetime import datetime

st.set_page_config(page_title="Incident Communication Assistant", layout="centered")
st.title("Incident Communication Assistant")
st.write("Create clear, consistent customer-facing messages during incidents.")

# Load API key securely
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# CSS to style buttons
st.markdown("""
<style>
div.stButton > button:first-child {
    margin: 0.5em 0.5em 0.5em 0;
}
button#clear-btn {
    background-color: #ff4b4b;
    color: white;
}
button#generate-btn {
    background-color: #28a745;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Initialize state
for key in ["incident_type", "severity", "affected_services", "summary", "generated_message"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# Form Inputs
st.session_state.incident_type = st.selectbox("Incident Type", ["System Outage", "Email Delay", "Service Degradation", "Security Event"], index=0)
st.session_state.severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], index=0)
st.session_state.affected_services = st.text_input("Affected Services", value=st.session_state.affected_services, placeholder="e.g. Inbound Email, Detection Engine")
st.session_state.summary = st.text_area("Incident Summary (Internal)", value=st.session_state.summary, placeholder="Free-form notes about incident scope and cause")

# Button row
col1, col2 = st.columns([1, 1])

with col1:
    clear_clicked = st.button("Clear Fields", key="clear-btn")
with col2:
    generate_clicked = st.button("Generate Message", key="generate-btn")

# Handle clear
if clear_clicked:
    for key in ["incident_type", "severity", "affected_services", "summary", "generated_message"]:
        st.session_state[key] = ""

# Handle generate
if generate_clicked:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    prompt = f"""
You are an assistant helping to write public-facing incident updates for customers.

Keep responses calm, concise, and factual. Avoid speculation or internal details. End with a support reminder if needed. Limit to 4 sentences.

Incident Type: {st.session_state.incident_type}
Severity: {st.session_state.severity}
Affected Services: {st.session_state.affected_services}
Summary: {st.session_state.summary}
Timestamp: {timestamp}

Update:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=250
        )
        st.session_state.generated_message = response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating message: {e}")

if st.session_state.generated_message:
    st.text_area("Generated Message", value=st.session_state.generated_message, height=200)
