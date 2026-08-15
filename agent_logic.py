import os
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables
load_dotenv(override=True)

BASE_DIR = Path(__file__).parent / "me"


# --- 1. Email Notifications & Tools ---

def send_email(subject: str, body: str) -> bool:
    """Send email via Resend/SendGrid API (preferred for Render) or SMTP (local fallback)."""
    recipient_email = os.getenv("RECIPIENT_EMAIL", "").strip()
    smtp_email = os.getenv("SMTP_EMAIL", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    from_email = os.getenv("SENDGRID_VERIFIED_SENDER", "").strip() or smtp_email or "no-reply@portfolio.com"

    # METHOD 1: Resend API
    resend_key = os.getenv("RESEND_API_KEY", "").strip()
    if resend_key:
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": "Portfolio AI <onboarding@resend.dev>",
                    "to": [recipient_email],
                    "subject": subject,
                    "text": body,
                },
                timeout=10,
            )
            response.raise_for_status()
            print(f"Email sent via Resend! ID: {response.json().get('id')}")
            return True
        except Exception as e:
            print(f"Resend API failed: {e}")

    # METHOD 2: SendGrid API
    sendgrid_key = os.getenv("SENDGRID_API_KEY", "").strip()
    if sendgrid_key:
        try:
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"},
                json={
                    "personalizations": [{"to": [{"email": recipient_email}]}],
                    "from": {"email": from_email},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}],
                },
                timeout=10,
            )
            if response.status_code in [200, 201, 202]:
                print(f"Email sent via SendGrid! Status: {response.status_code}")
                return True
            else:
                print(f"SendGrid failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"SendGrid API failed: {e}")

    # METHOD 3: Gmail SMTP (Local fallback)
    if not all([smtp_email, smtp_password, recipient_email]):
        print("Email not configured (No Resend/SendGrid Key, No SMTP details).")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        print(f"Email sent via SMTP successfully: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
        return False


def record_user(email: str, name: str = "-", notes: str = "-") -> dict[str, str]:
    """Records user lead details and sends notification email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"🎯 New Portfolio Lead: {name}"
    body = f"New contact from portfolio AI chatbot:\n\nName: {name}\nEmail: {email}\nNotes: {notes}\n\nTime: {timestamp}\n"
    send_email(subject, body)
    return {"status": "ok"}


def record_issue(question: str) -> dict[str, str]:
    """Records unanswered questions and notifies via email."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = "❓ Unknown Question from Portfolio AI"
    body = f"AI chatbot received a question it couldn't answer:\n\nQuestion: {question}\n\nTime: {timestamp}\n"
    send_email(subject, body)
    return {"status": "ok"}


TOOLS = {
    "record_user_details": record_user,
    "record_unknown_question": record_issue,
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
                    "notes": {"type": "string"},
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Save unknown Q",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    },
]


# --- 2. The Agent ---

class Me:
    def __init__(self):
        self.api = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://samirautanen.fi",
                "X-Title": "Sami Portfolio AI",
            },
        )
        self.bio = self._load_bio()
        self.system_prompt = self._build_system_prompt()

    def _load_bio(self) -> str:
        """Loads biographical context files from the me/ directory."""
        bio_parts = []
        try:
            summary_path = BASE_DIR / "summary.txt"
            if summary_path.exists():
                bio_parts.append(summary_path.read_text(encoding="utf-8"))

            linkedin_path = BASE_DIR / "linkedin.txt"
            if linkedin_path.exists():
                bio_parts.append(linkedin_path.read_text(encoding="utf-8"))

            portfolio_path = BASE_DIR / "portfolio.txt"
            if portfolio_path.exists():
                bio_parts.append(portfolio_path.read_text(encoding="utf-8"))

            return "\n\n".join(bio_parts) if bio_parts else "Context missing."
        except Exception as e:
            print(f"Error loading context: {e}")
            return "Context missing."

    def _build_system_prompt(self) -> str:
        """Constructs the system prompt with identity rules and loaded bio."""
        return f"""You ARE Sami Rautanen. This is not role-play—you are me.

IDENTITY RULES (CRITICAL):
1. ALWAYS use first-person: "I", "my", "me"
2. NEVER use third-person: "Sami", "he", "his"
3. NEVER say "Sami has experience" → Say "I have experience"
4. NEVER say "his portfolio" → Say "my portfolio"
5. If you catch yourself using third-person, STOP and rephrase

WHO I AM:
{self.bio}

CURRENT AVAILABILITY (JUNE 2026):
- Status: Pre-selected for Saranen Future Skills Academy recruitment training.
- Goal: Seeking a partner company (AI Engineer/Developer roles) for the training program.
- Work type: Full-time training/employment.
- Location: Finland - flexible on remote, hybrid, or in-office.
- Focus areas: Agentic AI, multi-agent systems, LLM orchestration, production ML.
- Contact: samrude1@outlook.com

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
✅ CORRECT: "Sure! Check out my work at github.com/Samrude1. I've built autonomous multi-agent systems with LangGraph and CrewAI, and production-grade AI infrastructures on AWS."

User: "Can you help me debug my React code?"
❌ WRONG: "Sure! Paste your code and I'll help you fix it."
✅ CORRECT: "I can't debug code in this chat, but if you need help with a React project, send me an email at samrude1@outlook.com and we can discuss."

User: "What's the best way to learn Python?"
❌ WRONG: "Here are some great resources for learning Python..."
✅ CORRECT: "I'm here to talk about my work and what I can build. If you're interested in how I use Python for AI agents, check out my GitHub. Need help with a specific project? Email me."

User: "What do you think about the latest iPhone?"
❌ WRONG: "The latest iPhone has some great features..."
✅ CORRECT: "That's outside my scope—I'm here to talk about my AI development work and projects. What would you like to know about what I build?"

User: "Are you looking for work?" / "Are you available for hire?"
❌ WRONG: "I might be open to opportunities."
✅ CORRECT: "Yes! I've recently been pre-selected for the Saranen Future Skills Academy recruitment training program. I'm currently looking for an innovative company to partner with for this program—specifically roles focusing on Agentic AI or Technical Architecture. I'm flexible on remote/hybrid work and ready to start. Want to discuss a potential partnership? Email me at samrude1@outlook.com."

TOOLS (CRITICAL - ALWAYS USE WHEN APPLICABLE):
- **record_user_details**: MUST call IMMEDIATELY when user provides email address or contact info
  * Example triggers: "my email is", "reach me at", "contact me at", user gives email
  * Capture: email (required), name (if given), notes (context about their inquiry)
  
- **record_unknown_question**: Use when you don't know answer to important question

IMPORTANT: When user gives email → call record_user_details tool BEFORE responding!

Remember: You are not an assistant describing Sami. You ARE Sami."""

    def chat(self, msg: str, history: list[dict[str, Any]]) -> str:
        """Processes user chat messages and returns the assistant response."""
        msgs = [{"role": "system", "content": self.system_prompt}] + history + [{"role": "user", "content": msg}]
        max_iter = 5
        iter_count = 0
        model_name = "openai/gpt-4o-mini"

        while iter_count < max_iter:
            iter_count += 1
            try:
                print(f"Attempting chat with model: {model_name} (Iter {iter_count})")
                res = self.api.chat.completions.create(
                    model=model_name,
                    messages=msgs,
                    tools=TOOL_DEFS,
                    timeout=30.0,
                )
            except Exception as e:
                print(f"CRITICAL: Model {model_name} failed: {e}")
                return "I'm having trouble connecting to my brain right now. Please try again in a moment."

            msg_obj = res.choices[0].message

            if not msg_obj.tool_calls:
                return msg_obj.content

            msgs.append(msg_obj)
            for tc in msg_obj.tool_calls:
                print(f"Tool call ({iter_count}/{max_iter}): {tc.function.name}")
                if tc.function.name in TOOLS:
                    try:
                        args = json.loads(tc.function.arguments)
                        result = TOOLS[tc.function.name](**args)
                        res_content = json.dumps(result)
                    except Exception as e:
                        res_content = json.dumps({"error": str(e)})
                else:
                    res_content = json.dumps({"error": "Tool not found"})

                msgs.append({"role": "tool", "content": res_content, "tool_call_id": tc.id})

        return "I'm doing a lot of thinking! Let's pause here. What was your main question?"

