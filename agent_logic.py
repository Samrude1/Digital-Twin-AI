import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

# --- 1. Tools & Actions ---
BASE_DIR = Path(__file__).parent / "me"

def push(msg): 
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    if token and user:
        requests.post("https://api.pushover.net/1/messages.json", data={"token": token, "user": user, "message": msg})
    else:
        print(f"Pushover not configured. Message: {msg}")

def record_user(email, name="-", notes="-"): 
    push(f"User: {name}, {email}, {notes}") 
    return {"status": "ok"}

def record_issue(question): 
    push(f"Unknown: {question}") 
    return {"status": "ok"}

TOOLS = {
    "record_user_details": record_user, 
    "record_unknown_question": record_issue
}

TOOL_DEFS = [
    {
        "type": "function", 
        "function": {
            "name": "record_user_details", 
            "description": "Save lead", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "email": {"type": "string"}, 
                    "name": {"type": "string"}, 
                    "notes": {"type": "string"}
                }, 
                "required": ["email"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "record_unknown_question", 
            "description": "Save unknown Q", 
            "parameters": {
                "type": "object", 
                "properties": {
                    "question": {"type": "string"}
                }, 
                "required": ["question"]
            }
        }
    }
]

# --- 2. The Agent ---
class Me:
    def __init__(self):
        self.api = OpenAI(
            api_key=os.getenv('GEMINI_API_KEY'), 
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Load Bio from text files
        self.bio = ""
        try:
            if (BASE_DIR / "summary.txt").exists():
                self.bio += (BASE_DIR / "summary.txt").read_text(encoding="utf-8") + "\n"
            
            if (BASE_DIR / "linkedin.txt").exists():
                self.bio += (BASE_DIR / "linkedin.txt").read_text(encoding="utf-8")
                
            if not self.bio:
                self.bio = "Context missing."
        except Exception as e:
            print(f"Error loading context: {e}")
            self.bio = "Context missing."

    def chat(self, msg, history):
        # history comes in as [{"role": "user", "content": "..."}] from api.py
        msgs = [{"role": "system", "content": f"Act as Sami Rautanen. Context:\n{self.bio}\nBe professional/engaging. Unknown ans: record_unknown_question. Lead: record_user_details."}] + history + [{"role": "user", "content": msg}]
        
        while True:
            res = self.api.chat.completions.create(model="gemini-2.0-flash", messages=msgs, tools=TOOL_DEFS)
            msg_obj = res.choices[0].message
            
            if not msg_obj.tool_calls: 
                return msg_obj.content
            
            msgs.append(msg_obj)
            for tc in msg_obj.tool_calls:
                print(f"Tool call: {tc.function.name}")
                if tc.function.name in TOOLS:
                    args = json.loads(tc.function.arguments)
                    result = TOOLS[tc.function.name](**args)
                    res_content = json.dumps(result)
                else:
                    res_content = json.dumps({"error": "Tool not found"})
                    
                msgs.append({"role": "tool", "content": res_content, "tool_call_id": tc.id})
