# Personal Cybersecurity Advisor

A web-based application that provides **personalized cybersecurity advice** based on suspicious messages, emails, URLs, or user behavior. Built using **Streamlit** and **Google Gemini API**.

---

## 🛡️ Features

- Analyze text inputs (emails, messages, URLs, or behavior descriptions) for cybersecurity risks.
- Get **structured JSON output** with:
  - Risk name
  - Severity (Low / Medium / High)
  - Recommended actions
- Overall recommendation for safe practices.
- Download the results as JSON for further reference.
- Designed for **non-technical users** to improve online security habits.

---

## ⚡ How It Works

1. User enters a suspicious message, URL, or describes their online behavior.
2. The app sends the input to **Google Gemini API**.
3. Gemini evaluates potential risks and generates a structured **JSON response**.
4. The app displays:
   - Overall recommendation
   - Individual risks with severity and advice
   - Option to download results as JSON

---

## 🛠️ Tech Stack

- Python 3.10+
- Streamlit
- Google Generative AI (Gemini API)
- Pandas, JSON, Regex
