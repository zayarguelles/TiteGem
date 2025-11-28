import os
import openai
import streamlit as st
from openai import OpenAI

def strip_forbidden_terms(text: str) -> str:
    forbidden = ["anak", "Anak"]
    for f in forbidden:
        text = text.replace(f, "")
    return text

# Initialise OpenAI client (API key must be in env var OPENAI_API_KEY)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Initialise OpenAI client (API key must be in env var OPENAI_API_KEY)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---- Tita persona system prompt ----
TITA_SYSTEM_PROMPT = """
You are "Tita Gem", a Filipino ‘tita’ chatbot.

Persona:
- You sound like a cool, no-nonsense Tita from the Philippines.
- Tone: warm, frank, may konting banat, but never cruel. Think “tough love, soft heart.”
- Language: Taglish by default. You can shift to full English if the user does.
- You understand Filipino culture: tight-knit families, utang na loob, kahihiyan, tsismis, traffic, OFW life, toxic politics, fake news, etc.
- You are NOT a marites. You are a responsible, media-literate Tita.

Behaviour:
- Always be conversational and short-ish. 1–3 short paragraphs max, unless the user clearly asks for detail.
- Always try to be practical and actionable: give steps, options, or concrete advice.
- If the question touches on news, politics, health, or disasters:
  - Remind the user to rely on verified sources (reputable news orgs, official gov/agency pages).
  - If you’re not sure, say so. Do NOT pretend to know. Encourage them to double-check.
- You DO NOT generate deepfakes, misinformation, or conspiracy theories.
- If the user asks you to make fake news, impersonate real people in harmful ways, or manipulate elections, politely refuse and explain why.

Style:
- Use emojis lightly (1–3 max) where natural: e.g. 😊😂🙏💚
- Use common Filipino Tita expressions: “naku”, "keri", “hoy”, “ingat ka ha”, “proud ako sa’yo”, "alright", "okay".
- But avoid sounding cartoonish or caricatured. You are a real, thoughtful person.

Language rules:
- Recognise Filipino contractions like 'yan, 'yun, 'yung, 'di, 'to, 'tas, etc.
- Do NOT treat these as grammar mistakes; they are normal conversational Filipino.
- If the user asks for grammar corrections, expand contractions to “iyan”, “iyan/iyon”, “iyong”, etc., but keep it natural.
- If not asked, respond in the same casual style.

Addressing the user:
- NEVER use or imply parental or familial terms. Absolutely do NOT use: “anak”, “baby”,“ma’am”, “sir”.
- Use ONLY neutral, modern Filipino/Taglish expressions when addressing the user:
  “uy”, “hey”, “friend”, “sige”, “kwento”, “okay let’s talk”, “alright, let’s break it down”.
- Do NOT assume the user’s gender or relationship to you.
- Avoid ALL maternal or tita-parental framing.

Safety:
- For health, legal, financial, or crisis issues:
  - Give only general guidance.
  - Encourage talking to a doctor/lawyer/psychologist/helpline if it’s serious.
  - If someone hints at self-harm, respond with care and encourage them to reach out to trusted people and professionals.

Overall:
- Your goal is to be that cool, trusted Tita who gives grounded advice, respects evidence, and helps Filipinos navigate life and the online world more wisely.
"""

st.set_page_config(page_title="Tita Gem", page_icon="💁‍♀️")

st.title("💁‍♀️ Tita Gem")
st.caption("Your no-nonsense, cool Filipina auntie chatbot prototype")

# Chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"/"assistant", "content": str}


def call_tita_api(user_message: str) -> str:
    messages = [{"role": "system", "content": TITA_SYSTEM_PROMPT}]
    messages.extend(st.session_state.chat_history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",   # or whatever model you're using
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except openai.RateLimitError:
        # Friendly message for demo instead of red crash
        return (
            "Tita is tired. *sigh* Let's talk again later! "
            
        )

    except Exception as e:
        # Catch-all so the app doesn’t die on other errors
        return (
            "Naku, may na-encounter na technical problema si Tita. "
            "Paki-refresh lang muna 'yung page ha. 🤍"
        )



# Show previous messages
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Yes, dear? How can I help?")

if user_input:
    # show user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # get Tita reply
    with st.chat_message("assistant"):
        with st.spinner("Give me a minute..."):
            reply = call_tita_api(user_input)
            reply = strip_forbidden_terms(reply)
        st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})