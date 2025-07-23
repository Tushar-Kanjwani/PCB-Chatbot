import pymysql
import csv
from functools import lru_cache
from together import Together
import os

# --- MySQL configuration (adjust as needed) ---
# For Vercel deployment, you'll need to use a cloud database service
# like PlanetScale, Railway, or AWS RDS
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "KjGYJelGnozfTkOraNeoxRUFwoCRGLpX"),
    "database": os.getenv("DB_NAME", "railway")
}



def get_db_connection():
    """Establishes a new connection to the MySQL database."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return None

def get_cached_response(user_query: str):
    """Returns a previously stored response for this query, if any."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT model_response FROM chat_logs WHERE user_query = %s "
            "ORDER BY created_at DESC LIMIT 1",
            (user_query,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[CACHE ERROR] {e}")
        return None
    finally:
        conn.close()

def log_chat(user_query: str, model_response: str, total_tokens: int):
    """Logs a new question/answer into chat_logs."""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (user_query, model_response, total_tokens) "
            "VALUES (%s, %s, %s)",
            (user_query, model_response, total_tokens)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"[LOG ERROR] {e}")
    finally:
        conn.close()

@lru_cache(maxsize=1)
def load_context():
    """Loads and formats the PCB.csv into a single text blob."""
    try:
        lines = []
        with open("PCB.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            mapping = {
                "Player":"Player","Starting Year":"First Match","Ending Year":"Last Match",
                "Matches Played":"Matches","Innings Batted":"Innings","Not Outs":"Not Outs",
                "Runs Scored":"Runs","Highest Score":"Highest Score","Average Score":"Average",
                "Centuries":"100s","Half-centuries":"50s","Ducks":"Ducks"
            }
            
            for row in reader:
                parts = []
                for col, value in row.items():
                    # Skip unnamed columns
                    if col.startswith("Unnamed"):
                        continue
                    label = mapping.get(col, col)
                    parts.append(f"{label}: {value}")
                lines.append(", ".join(parts))
        return "\n".join(lines)
    except Exception as e:
        print(f"[CONTEXT ERROR] {e}")
        return "Error loading cricket data. Please try again later."

# Initialize Together client & context
api_key = os.getenv("TOGETHER_API_KEY", "tgp_v1_2qPAm5jNcqlwanhcusx0I2Ir7K9ECz8z3vmJFWcsGqM")
client = Together(api_key=api_key)
context_data = load_context()

def answer_query(user_query: str) -> tuple[str, int]:
    """
    Returns (answer, total_tokens).  
    Uses caching first; if not found, calls the LLM and logs the result.
    """
    # 1) Try cache
    cached = get_cached_response(user_query)
    if cached:
        return cached, 0

    # 2) Otherwise, ask the model
    try:
        resp = client.chat.completions.create(
            model="lgai/exaone-3-5-32b-instruct",
            max_tokens=512,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant who answers questions about cricket players from a dataset."
                },
                {
                    "role": "user",
                    "content": f"Here is the dataset:\n\n{context_data}\n\nNow answer this question:\n{user_query}"
                }
            ]
        )
        answer = resp.choices[0].message.content
        total = getattr(resp.usage, "total_tokens", 0) if hasattr(resp, "usage") else 0

        # 3) Log and return
        log_chat(user_query, answer, total)
        return answer, total
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return "Sorry, I'm having trouble processing your request right now. Please try again later.", 0
