# pylint: disable = invalid-name
import os
import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from agents.agent import Agent
import time
import random
from streamlit_autorefresh import st_autorefresh


def update_quote():
    quotes = [
        "Travel is the only thing you buy that makes you richer.",
        "The world is a book and those who do not travel read only one page.",
        "Jobs fill your pockets, adventures fill your soul.",
        "Life is short and the world is wide.",
        "Travel far enough, you meet yourself."
    ]

    # Initialize quote index and timestamp if not present
    if 'quote_index' not in st.session_state:
        st.session_state.quote_index = 0
        st.session_state.last_quote_time = time.time()
    
    # Rotate quote every 7 seconds
    if time.time() - st.session_state.last_quote_time > 7:
        st.session_state.quote_index = (st.session_state.quote_index + 1) % len(quotes)
        st.session_state.last_quote_time = time.time()

    return quotes[st.session_state.quote_index]

def populate_envs(sender_email, receiver_email, subject):
    # os.environ['FROM_EMAIL'] = sender_email
    # os.environ['TO_EMAIL'] = receiver_email
    # os.environ['EMAIL_SUBJECT'] = subject
    st.session_state['FROM_EMAIL'] = sender_email
    st.session_state['TO_EMAIL'] = receiver_email
    st.session_state['EMAIL_SUBJECT'] = subject


def send_email(sender_email, receiver_email, subject, thread_id):
    try:
        populate_envs(sender_email, receiver_email, subject)
        config = {'configurable': {'thread_id': thread_id}}
        st.session_state.agent.graph.invoke(None, config=config)
        st.success('Email sent successfully!')
        # Clear session state
        for key in ['travel_info', 'thread_id']:
            st.session_state.pop(key, None)
    except Exception as e:
        st.error(f'Error sending email: {e}')


def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()


def render_custom_css():
    st.markdown(
        '''
        <style>
        /* ✈️ Fly-in animation */
        @keyframes fly-in {
            0% {
                transform: translateX(-150px) rotate(-20deg);
                opacity: 0;
            }
            50% {
                opacity: 1;
            }
            100% {
                transform: translateX(0px) rotate(0deg);
            }
        }

        .emoji-fly {
            display: inline-block;
            animation: fly-in 2s ease-out forwards;
            margin-right: 0.3em;
        }

        /* 🌍 Spin animation */
        @keyframes rotate-globe {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .emoji-spin {
            display: inline-block;
            animation: rotate-globe 4s linear infinite;
            margin-right: 0.3em;
        }

        .main-title {
            font-size: 2.5em;
            color: #333;
            text-align: center;
            margin-bottom: 0.5em;
            font-weight: bold;
        }

        .sub-title {
            font-size: 1.2em;
            color: #333;
            text-align: left;
            margin-bottom: 0.5em;
        }

        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        .query-box {
            width: 80%;
            max-width: 600px;
            margin-top: 0.5em;
            margin-bottom: 1em;
        }

        .query-container {
            width: 80%;
            max-width: 600px;
            margin: 0 auto;
        }
        </style>
        ''', unsafe_allow_html=True
    )




def render_ui():
    quote = update_quote()  

    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    st.markdown('''
    <div class="center-container">
        <div class="main-title">
            <span class="emoji-fly">✈️</span>
            <span class="emoji-spin">🌍</span>
            AI Travel Agent 
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="query-container">', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enter your travel query and get flight and hotel information:</div>', unsafe_allow_html=True)
    
    user_input = st.text_area(
        'Travel Query',
        height=200,
        key='query',
        placeholder='Type your travel query here...',
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.image("images/ai-travel.png", use_column_width=True)
    st.sidebar.markdown("### AI Travel Assistant")
    st.sidebar.markdown(f"""
    <div style="
        margin-top: 1.2em;
        font-size: 1.1rem;
        font-style: italic;
        font-weight: 500;
        color: #2c3e50;
        background: linear-gradient(to right, #e0f7fa, #fce4ec);
        padding: 12px 16px;
        border-radius: 10px;
        animation: fadeIn 1.5s ease-in-out;
    ">
        “{quote}”
    </div>

    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """, unsafe_allow_html=True)


    return user_input



def process_query(user_input):
    if user_input:
        try:
            thread_id = str(uuid.uuid4())
            st.session_state.thread_id = thread_id

            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            result = st.session_state.agent.graph.invoke({'messages': messages}, config=config)

            st.subheader('Travel Information')
            st.write(result['messages'][-1].content)

            st.session_state.travel_info = result['messages'][-1].content

        except Exception as e:
            st.error(f'Error: {e}')
    else:
        st.error('Please enter a travel query.')


def render_email_form():
    send_email_option = st.radio('Do you want to send this information via email?', ('No', 'Yes'))
    if send_email_option == 'Yes':
        with st.form(key='email_form'):
            sender_email = st.text_input('Sender Email')
            receiver_email = st.text_input('Receiver Email')
            subject = st.text_input('Email Subject', 'Travel Information')
            submit_button = st.form_submit_button(label='Send Email')

        if submit_button:
            if sender_email and receiver_email and subject:
                send_email(sender_email, receiver_email, subject, st.session_state.thread_id)
            else:
                st.error('Please fill out all email fields.')


def main():
    initialize_agent()
    render_custom_css()
    user_input = render_ui()


    if st.button('Get Travel Information'):
        process_query(user_input)

    if 'travel_info' in st.session_state:
        render_email_form()


if __name__ == '__main__':
    main()
