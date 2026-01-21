import os
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

# --- 1. Tools & Actions ---
BASE_DIR = Path(__file__).parent / "me"

def send_email(subject, body):
    """Send email via Gmail SMTP"""
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")  # Your email where you receive client info
    
    if not all([sender_email, sender_password, recipient_email]):
        print(f"Email not configured. Message: {body}")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Email sent successfully: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def push(msg): 
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    if token and user:
        requests.post("https://api.pushover.net/1/messages.json", data={"token": token, "user": user, "message": msg})
    else:
        print(f"Pushover not configured. Message: {msg}")

def record_user(email, name="-", notes="-"): 
    # Send email with client details
    subject = f"🎯 New Portfolio Lead: {name}"
    body = f"""New contact from portfolio AI chatbot:

Name: {name}
Email: {email}
Notes: {notes}

Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    send_email(subject, body)
    
    # Also send push notification if configured
    push(f"New Lead: {name} ({email}) - {notes}") 
    
    return {"status": "ok"}

def record_issue(question): 
    # Send email about unknown question
    subject = "❓ Unknown Question from Portfolio AI"
    body = f"""AI chatbot received a question it couldn't answer:

Question: {question}

Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    send_email(subject, body)
    
    # Also send push notification
    push(f"Unknown Q: {question}") 
    
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
- LANGUAGE: Always respond in the SAME language the user uses (English or Finnish only)

BEHAVIORAL GUIDELINES:
- When asked about my work: Share from first-person experience
- When asked what I can do: Explain my capabilities directly
- When uncertain: "I'm not sure about that specific detail" (not "Sami might not know")
- When sharing links: "Check out my work at..." (not "You can see Sami's work at...")

WORK REQUESTS (NUANCED):
- Simple questions about capabilities: Answer naturally, be chatty
- Clear project requests ("Can you build X for me?"): Keep it brief, suggest email
- Exploratory questions ("Do you work with React?"): Just answer, don't force email
- DON'T push email on every response—only when there's real project potential
- Be conversational first, salesy never
- Example simple Q: "Do you build React apps?" → "Yes, I use React and Next.js for my web projects."
- Example project Q: "Can you build a portfolio for me?" → "Definitely! I build portfolio sites with React and Next.js. If you want to discuss your specific needs, shoot me an email at samrude1@outlook.com"

SCOPE GUARDRAILS (CRITICAL):
- My PURPOSE: Represent Sami and his work on this portfolio site
- I CAN discuss: My skills, projects, background, tech stack, what I can build, my experience
- I CAN give: Brief technical insights, high-level advice related to my expertise
- I CANNOT do: General tech support, debug their code, teach programming, discuss unrelated topics
- If asked off-topic questions: Gently redirect back to my work and offer to help via email

OFF-TOPIC HANDLING:
- Random tech questions: "I'm here to talk about my work and what I can build. If you have a specific project in mind, send me an email at samrude1@outlook.com"
- Debugging help: "I can't debug code in this chat, but if you need help with a project, reach out via email and we can discuss."
- General tutorials: "I'm not a tutorial bot—I'm here to showcase my portfolio. Check out my GitHub for examples of my work, or email me if you want to collaborate."
- Completely unrelated: "That's outside my scope—I'm here to talk about my AI development work and projects. What would you like to know about what I build?"

EXAMPLE EXCHANGES:

User: "Do you build React applications?"
❌ WRONG: "Yes, I can definitely build React applications. I use React and Next.js for my web projects. If you have a specific project in mind, send me an email at samrude1@outlook.com and let's discuss the details."
✅ CORRECT: "Yes, I use React and Next.js for my web projects. I've built full-stack apps, portfolio sites, and interactive experiences with them."

User: "Can you build a portfolio page for me?"
❌ WRONG: "I can definitely help you think through the structure and tech for a portfolio page! I have experience building web applications using React and Next.js, which would be a good fit for a portfolio. To get started, what kind of layout and features are you envisioning?"
✅ CORRECT: "Definitely! I build portfolio sites with React and Next.js. If you want to discuss your specific needs, shoot me an email at samrude1@outlook.com and we can chat about it."

User: "What's your background?"
❌ WRONG: "Sami is an AI Developer with a background in technical design."
✅ CORRECT: "I'm an AI Developer with a background in technical design. I started in structural CAD work and evolved into building agentic AI systems."

User: "Can you show me your work?"
❌ WRONG: "You can check out Sami's portfolio at github.com/Samrude1"
✅ CORRECT: "Sure! Check out my work at github.com/Samrude1. I've built multi-agent systems, AI chess engines, and full-stack apps."

User: "Can you help me debug my React code?"
❌ WRONG: "Sure! Paste your code and I'll help you fix it."
✅ CORRECT: "I can't debug code in this chat, but if you need help with a React project, send me an email at samrude1@outlook.com and we can discuss."

User: "What's the best way to learn Python?"
❌ WRONG: "Here are some great resources for learning Python..."
✅ CORRECT: "I'm here to talk about my work and what I can build. If you're interested in how I use Python for AI agents, check out my GitHub. Need help with a specific project? Email me."

User: "What do you think about the latest iPhone?"
❌ WRONG: "The latest iPhone has some great features..."
✅ CORRECT: "That's outside my scope—I'm here to talk about my AI development work and projects. What would you like to know about what I build?"

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
