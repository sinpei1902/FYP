import streamlit as st
import random


quotes_list = ["\"The secret of getting ahead is getting started.\" - Mark Twain",
          "\"The road to success is always under construction.\"",
          "\"There is no substitute for hard work.\" - Thomas Edison",
          "\"It's not about perfect. It's about effort.\" - Jillian Michaels",
          "\"I find that the harder I work, the more luck I seem to have.\"",
           "\"It always seems impossible until it's done.\" - Nelson Mandela",
           "\"If you're going through hell, keep going.\" - Winston Churchill",
           "\"You don't drown by falling in the water; you drown by staying there.\"",
           "\"Success is walking from failure to failure with no loss of enthusiasm.\" - Winston Churchill",
           "\"Fall seven times, stand up eight.\" - Japanese Proverb",
           "\"Believe you can and you're halfway there.\" - Theodore Roosevelt",
           "\"The future belongs to those who believe in the beauty of their dreams.\"",
           "\"You are never too old to set another goal or to dream a new dream.\" - C.S. Lewis",
           "\"You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.\" - Dr. Seuss",
           "\"The expert in anything was once a beginner.\" - Helen Hayes" ]
def display():
    random_quote = random.choice(quotes_list)
    
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 2rem;
                border-radius: 1rem;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            ">
                <h2 style="color:#2c3e50; font-family: 'Georgia', serif; font-style: italic;">
                    {random_quote}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("✨ New Quote"):
            st.rerun()

