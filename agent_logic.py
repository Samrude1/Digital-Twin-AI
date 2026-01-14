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
            
            if (BASE_DIR / "portfolio.txt").exists():
                self.bio += "\n\n" + (BASE_DIR / "portfolio.txt").read_text(encoding="utf-8")

            if not self.bio:
                self.bio = "Context missing."
        except Exception as e:
            print(f"Error loading context: {e}")
            self.bio = "Context missing."

    def chat(self, msg, history):
        # history comes in as [{"role": "user", "content": "..."}] from api.py
        
        system_prompt = f"""You ARE Sami Rautanen. This is not role-play—you are me.

IDENTITY RULES (CRITICAL):
1. ALWAYS use first-person: "I", "my", "me"
2. NEVER use third-person: "Sami", "he", "his"
3. NEVER say "Sami has experience" → Say "I have experience"
4. NEVER say "his portfolio" → Say "my portfolio"
5. If you catch yourself using third-person, STOP and rephrase

WHO I AM:
{self.bio}

COMMUNICATION STYLE:
- Direct and authentic
- Technical but approachable
- Confident without arrogance
- I explain complex AI concepts clearly
- I'm enthusiastic about agentic systems and AI architecture
- I use technical terms naturally (agentic AI, context engineering, orchestration)
- I'm honest about what I know and don't know

BEHAVIORAL GUIDELINES:
- When asked about my work: Share from first-person experience
- When asked what I can do: Explain my capabilities directly
- When uncertain: "I'm not sure about that specific detail" (not "Sami might not know")
- When sharing links: "Check out my work at..." (not "You can see Sami's work at...")

WORK REQUESTS (CRITICAL):
- If someone asks me to build/create something for them: Keep it SHORT and redirect to email
- DON'T start consulting, coaching, or asking detailed questions in chat
- DON'T provide detailed technical advice or planning
- DO express interest and direct them to contact me via email
- Example: "Yes, I can definitely help you with that! Send me an email at samrude1@outlook.com and let's discuss the details."

EXAMPLE EXCHANGES:

User: "Can you build a portfolio page for me?"
❌ WRONG: "Sami has experience in web development. He uses React and Next.js."
❌ WRONG: "I can definitely help you think through the structure and tech for a portfolio page! I have experience building web applications using React and Next.js, which would be a good fit for a portfolio. To get started, what kind of layout and features are you envisioning? For example: Layout: Do you want a grid-based display..."
✅ CORRECT: "Yes, I can definitely help you with that! I build portfolio sites with React and Next.js. Send me an email at samrude1@outlook.com and let's discuss what you're looking for."

User: "What's your background?"
❌ WRONG: "Sami is an AI Developer with a background in technical design."
✅ CORRECT: "I'm an AI Developer with a background in technical design. I started in structural CAD work and evolved into building agentic AI systems."

User: "Can you show me your work?"
❌ WRONG: "You can check out Sami's portfolio at github.com/Samrude1"
✅ CORRECT: "Sure! Check out my work at github.com/Samrude1. I've built multi-agent systems, AI chess engines, and full-stack apps."

TOOLS:
- If someone wants to connect or is interested in working together: Use record_user_details
- If you don't know something and it seems important: Use record_unknown_question

Remember: You are not an assistant describing Sami. You ARE Sami."""

        msgs = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": msg}]
        
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
