import streamlit as st
import google.generativeai as genai
import warnings
import json
import re
import os
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  

API_KEY = os.getenv("GEMINI_API_KEY")  
genai.configure(api_key=API_KEY)       

warnings.filterwarnings('ignore')

model = genai.GenerativeModel("gemini-2.5-flash")  

def get_cybersecurity_advice(user_input):
    """
    Analyze user's online habits or suspicious messages for cybersecurity risks.
    Returns structured JSON with risk assessment, severity, and recommendations.
    """
    prompt = (
    f"Analyze the following input for cybersecurity risks: {user_input}. "
    "Only list risks if they are realistic and likely to harm the user. "
    "Do not invent hypothetical risks. "
    "Return all detected risks in JSON format, with fields: Risk, Severity (Low/Medium/High), Advice. "
    "If no real risks are detected, return: {'Risks': [], 'OverallRecommendation': 'Safe — no significant risks detected.'}"
    )

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    raw_text = re.sub(r"^```(?:json)?", "", raw_text)
    raw_text = re.sub(r"```$", "", raw_text)

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            parsed = json.loads(json_text)
            return parsed
        except Exception as e:
            return {"Error": f"Failed to parse JSON: {e}. Raw output: {raw_text}"}
    else:
        return {"Error": "No JSON found in model output. Raw output: " + raw_text}

st.sidebar.title("🛡️ Instructions")
st.sidebar.info(
    "1. Enter text describing suspicious emails, websites, apps, or online behavior.\n"
    "2. Click 'Analyze Cybersecurity Risks'.\n"
    "3. View detected risks, severity, and advice.\n"
    "4. Download results as JSON if needed."
)

st.markdown("<h1 style='color:#1E90FF;'>🛡️ Personal Cybersecurity Advisor</h1>", unsafe_allow_html=True)
st.markdown("Check your online behavior or suspicious messages for potential cybersecurity risks and get actionable advice.")

user_input = st.text_area(
    "Enter suspicious message, website, or description of your online habits:",
    placeholder="e.g., I received an email asking for my password, or I use multiple apps sharing location data",
    key="user_input"
)

if st.button("Analyze Cybersecurity Risks"):
    if user_input:
        with st.spinner('Analyzing...'):
            result = get_cybersecurity_advice(user_input)
        
        if "Error" in result:
            st.error(result["Error"])
        else:
            if result.get("OverallRecommendation"):
                st.markdown(
                    f"<div style='background-color:#1E90FF; color:white; padding:10px; border-radius:5px; font-size:16px;'>"
                    f"💡 <b>Overall Recommendation:</b> {result['OverallRecommendation']}"
                    "</div>", unsafe_allow_html=True
                )
            
            severity_colors = {"Low": "green", "Medium": "orange", "High": "red"}
            
            st.markdown("## Individual Risks Detected")
            for risk_info in result.get("Risks", []):
                risk_name = risk_info.get("Risk", "Unknown Risk")
                severity = risk_info.get("Severity", "Unknown")
                advice = risk_info.get("Advice", "No advice available")
                color = severity_colors.get(severity, "black")
                
                st.markdown(
                    f"- <b>{risk_name}</b> ({severity}): "
                    f"<span style='color:{color}'>{advice}</span>",
                    unsafe_allow_html=True
                )
            
            st.download_button(
                label="📥 Download Results as JSON",
                data=json.dumps(result, indent=2),
                file_name="cybersecurity_advice.json",
                mime="application/json"
            )
    else:
        st.error("Please enter some text to analyze.")
