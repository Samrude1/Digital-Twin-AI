from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader

# Load environment variables
load_dotenv(override=True)

def push(text):
    if os.getenv("PUSHOVER_TOKEN"):
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": os.getenv("PUSHOVER_TOKEN"),
                    "user": os.getenv("PUSHOVER_USER"),
                    "message": text,
                }
            )
        except Exception as e:
            print(f"Pushover failed: {e}")

def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]


class Me:
    def __init__(self):
        # Use OpenAI client but point to Gemini API if that's what was intended
        # Or standard OpenAI if GEMINI_API_KEY is actually an OpenAI key?
        # The original code used base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        # which implies using Google's OpenAI-compatible endpoint.
        
        self.openai = OpenAI(
            api_key=os.environ.get('GEMINI_API_KEY'),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.name = "Sami Rautanen"
        
        # Load LinkedIn context
        self.linkedin = ""
        try:
            if os.path.exists("me/linkedin.txt"):
                with open("me/linkedin.txt", "r", encoding="utf-8") as f:
                    self.linkedin = f.read()
        except Exception as e:
            print(f"Warning: Could not read linkedin.txt: {e}")

        # Load Summary context
        self.summary = ""
        try:
            with open("me/summary.txt", "r", encoding="utf-8") as f:
                self.summary = f.read()
        except Exception as e:
            print(f"Warning: Could not read summary.txt: {e}")


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments)
                print(f"Tool called: {tool_name}", flush=True)
                tool = globals().get(tool_name)
                result = tool(**arguments) if tool else {}
                results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
            except Exception as e:
                print(f"Tool execution failed: {e}")
                results.append({"role": "tool", "content": json.dumps({"error": str(e)}), "tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, answer their question first, then delicately try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}. Keep your answers concise and punchy for a web chat interface."
        return system_prompt
    
    def chat(self, message, history):
        # history is expected to be a list of {"role": "user"|"assistant", "content": "..."}
        
        # Filter strictly for user/assistant roles to be safe for API
        valid_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in history 
            if msg["role"] in ["user", "assistant"]
        ]

        messages = [{"role": "system", "content": self.system_prompt()}] + valid_history + [{"role": "user", "content": message}]
        
        # Max turns safe-guard
        turns = 0
        max_turns = 5 
        
        done = False
        final_content = ""

        while not done and turns < max_turns:
            turns += 1
            response = self.openai.chat.completions.create(model="gemini-1.5-flash", messages=messages, tools=tools)
            
            choice = response.choices[0]
            
            if choice.finish_reason == "tool_calls":
                message_obj = choice.message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                
                # We need to append the tool call message AND the tool results to conversation
                messages.append(message_obj)
                messages.extend(results)
            else:
                final_content = choice.message.content
                done = True
                
        return final_content
