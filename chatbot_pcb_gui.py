import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from together import Together

# MySQL config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "chatbot_db"
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def get_cached_response(user_query):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT model_response FROM chat_logs WHERE user_query = %s ORDER BY created_at DESC LIMIT 1",
            (user_query,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return result[0]
    return None

def log_chat(user_query, model_response, total_tokens):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_logs (user_query, model_response, total_tokens)
            VALUES (%s, %s, %s)
            """,
            (user_query, model_response, total_tokens)
        )
        conn.commit()
        cursor.close()
        conn.close()

# Load and prepare context from CSV (only once)
@st.cache_data
def load_context():
    df = pd.read_csv("PCB.csv")
    df = df.drop(columns=["Unnamed: 12", "Unnamed: 13", "Unnamed: 14", "Unnamed: 15"], errors='ignore')
    column_mapping = {
        "Player": "Player",
        "Starting Year": "First Match",
        "Ending Year": "Last Match",
        "Matches Played": "Matches",
        "Innings Batted": "Innings",
        "Not Outs": "Not Outs",
        "Runs Scored": "Runs",
        "Highest Score": "Highest Score",
        "Average Score": "Average",
        "Centuries": "100s",
        "Half-centuries": "50s",
        "Ducks": "Ducks"
    }
    context_data = "\n".join([
        ", ".join([f"{column_mapping.get(col, col)}: {row[col]}" for col in df.columns])
        for _, row in df.iterrows()
    ])
    return context_data

context_data = load_context()

# LLM client
client = Together(api_key="tgp_v1_2qPAm5jNcqlwanhcusx0I2Ir7K9ECz8z3vmJFWcsGqM")

# Streamlit UI
st.set_page_config(page_title="PCB Chatbot", page_icon=":cricket_bat_and_ball:", layout="wide")
st.title("🏏 PCB Chatbot")
st.write("Ask a question about Pakistan cricket players!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_query = st.text_input("Your question:", key="user_input", on_change=None)

if st.button("Ask") and user_query.strip():
    st.session_state.chat_history.append(("You", user_query))
    cached = get_cached_response(user_query)
    if cached:
        st.session_state.chat_history.append(("Bot", cached))
    else:
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="lgai/exaone-3-5-32b-instruct",
                    max_tokens=512,
                    messages=[
                        {"role": "system", "content": "You are an assistant who answers questions about cricket players from a dataset."},
                        {"role": "user", "content": f"Here is the dataset:\n\n{context_data}\n\nNow answer this question:\n{user_query}"}
                    ]
                )
                answer = response.choices[0].message.content
                total_tokens = None
                if hasattr(response, 'usage') and response.usage is not None:
                    total_tokens = getattr(response.usage, 'total_tokens', None)
                st.session_state.chat_history.append(("Bot", answer))
                log_chat(user_query, answer, total_tokens)
            except Exception as e:
                st.session_state.chat_history.append(("Bot", f"Error: {str(e)}"))

# Display chat history
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")