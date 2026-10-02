import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


# --------------------------------
# APP CONFIGURATION
# --------------------------------

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
)


# --------------------------------
# SECRETS
# --------------------------------

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]

GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# --------------------------------
# GEMINI CLIENT
# --------------------------------

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


# --------------------------------
# GEMINI CHAT
# --------------------------------

def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)

        return response.text

    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# --------------------------------
# EMAIL FUNCTION
# --------------------------------

def send_email(to_address, subject, body):

    message = MIMEText(
        body,
        "plain",
        "utf-8"
    )

    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD
        )

        server.send_message(message)


# --------------------------------
# MESSAGE DISPLAY
# --------------------------------

def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            st.write(
                message["content"]
            )

        elif message["kind"] == "image":

            st.image(
                message["content"]
            )


# --------------------------------
# ADD MESSAGE
# --------------------------------

def add_message(role, kind, content):

    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )

    render_message(
        st.session_state.messages[-1]
    )


# --------------------------------
# ONBOARDING
# --------------------------------

if "onboarded" not in st.session_state:

    st.title("📚 Snap & Study")

    st.caption(
        "Upload it. Understand it. Learn it."
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name",
            placeholder="Enter your name"
        )

        email = st.text_input(
            "Your email address",
            placeholder="you@example.com"
        )

        submitted = st.form_submit_button(
            "Let's Study 🚀",
            use_container_width=True
        )

    if submitted:

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

        elif not email.strip():

            st.warning(
                "Please enter your email address."
            )

        else:

            st.session_state.name = (
                name.strip()
            )

            st.session_state.email = (
                email.strip()
            )

            st.session_state.chat = (
                gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
            )

            st.session_state.messages = []

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# --------------------------------
# MAIN HEADER
# --------------------------------

st.title("📚 Snap & Study")

st.caption(
    f"Logged in as {st.session_state.name}"
)


# --------------------------------
# EMAIL SUMMARY BUTTON
# --------------------------------

if len(st.session_state.messages) > 2:

    if st.button(
        "📧 Send Study Summary to Email",
        use_container_width=True
    ):

        with st.spinner(
            "Creating your study summary..."
        ):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        try:

            send_email(
                st.session_state.email,
                "📚 Your Snap & Study Summary",
                summary
            )

            st.success(
                "Study summary sent to your email! 📧"
            )

        except Exception as error:

            st.error(
                f"Couldn't send the email: {error}"
            )


# --------------------------------
# CHAT HISTORY
# --------------------------------

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# --------------------------------
# CHAT INPUT
# --------------------------------

user_input = st.chat_input(
    "Ask a question, or attach a study photo",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ],
)


# --------------------------------
# HANDLE USER INPUT
# --------------------------------

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # ----------------------------
    # IMAGE
    # ----------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # ----------------------------
    # TEXT
    # ----------------------------

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)


    # ----------------------------
    # IMAGE WITHOUT TEXT
    # ----------------------------

    elif photo is not None:

        parts.append(
            "Explain this study material "
            "clearly and help me understand "
            "it step by step."
        )


    # ----------------------------
    # GEMINI RESPONSE
    # ----------------------------

    with st.spinner(
        "Understanding your study material..."
    ):

        answer = ask_gemini(parts)


    add_message(
        "assistant",
        "text",
        answer
    )