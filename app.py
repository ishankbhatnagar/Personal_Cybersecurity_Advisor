import streamlit as st
import google.generativeai as genai
import warnings
import os
import json
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

warnings.filterwarnings('ignore')

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

knowledge_folder = "knowledge_docs"
knowledge_texts = []
knowledge_filenames = []

for fname in os.listdir(knowledge_folder):
    if fname.endswith(".txt"):
        path = os.path.join(knowledge_folder, fname)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            knowledge_texts.append(text)
            knowledge_filenames.append(fname)

knowledge_embeddings = np.array([embed_model.encode(t) for t in knowledge_texts], dtype='float32')

embedding_dim = knowledge_embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_dim)
index.add(knowledge_embeddings)

def retrieve_docs(query, top_k=3, similarity_threshold=0.5):
    query_vec = np.array([embed_model.encode(query)], dtype='float32')
    distances, indices = index.search(query_vec, top_k)
    
    docs = []
    sources = []
    
    for dist, idx in zip(distances[0], indices[0]):
        similarity = 1 / (1 + dist)  
        if similarity >= similarity_threshold:
            docs.append(knowledge_texts[idx])
            sources.append(knowledge_filenames[idx])
    
    return docs, sources


def get_cybersecurity_advice(user_input):
    """
    Retrieve top knowledge docs, combine with user input, and ask Gemini for advice
    """
    top_docs, sources = retrieve_docs(user_input)
    context_text = "\n".join(top_docs)
    
    prompt = (
        f"User input:\n{user_input}\n\n"
        f"Relevant cybersecurity knowledge:\n{context_text}\n\n"
        "Analyze the user's input for realistic cybersecurity risks. "
        "Only list actual risks, severity (Low/Medium/High), and actionable advice. "
        "Return the response in JSON format like:\n"
        "{'Risks':[{'Risk':'...','Severity':'...','Advice':'...'}], "
        "'OverallRecommendation':'...'} "
        "If no risks are detected, return: {'Risks': [], 'OverallRecommendation': 'Safe — no significant risks detected.'}"
    )

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    raw_text = re.sub(r"^```(?:json)?", "", raw_text)
    raw_text = re.sub(r"```$", "", raw_text)
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            parsed = json.loads(json_text)
            parsed["Sources"] = sources  # Add sources info
            return parsed
        except Exception as e:
            return {"Error": f"Failed to parse JSON: {e}. Raw output: {raw_text}"}
    else:
        return {"Error": "No JSON found in model output. Raw output: " + raw_text}

st.sidebar.title("🛡️ Instructions")
st.sidebar.info(
    "1. Enter suspicious emails, websites, apps, or online behavior.\n"
    "2. Click 'Analyze Cybersecurity Risks'.\n"
    "3. View detected risks, severity, advice, and sources.\n"
    "4. Download results as JSON if needed."
)

st.markdown("<h1 style='color:#1E90FF;'>🛡️ Personal Cybersecurity Advisor (RAG)</h1>", unsafe_allow_html=True)
st.markdown("Enter suspicious messages, websites, or your online behavior to detect potential cybersecurity risks and get actionable advice.")

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
            
            st.markdown("## ⚠️ Individual Risks Detected")
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

            if result.get("Sources"):
                st.markdown("## 📚 Sources / References")
                for src in result["Sources"]:
                    st.markdown(f"- {src}")
            
            st.download_button(
                label="📥 Download Results as JSON",
                data=json.dumps(result, indent=2),
                file_name="cybersecurity_advice.json",
                mime="application/json"
            )
    else:
        st.error("Please enter some text to analyze.")
