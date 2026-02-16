import os
from groq import Groq
from dotenv import load_dotenv
from app.policy import policy
from app.memory import get_user_profile

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_reply(subject, body, user_id):
    profile = get_user_profile(user_id)

    profile_context = "\n".join([
        f"User Name: {profile.get('name', '')}",
        f"Designation: {profile.get('designation', '')}",
        f"Company: {profile.get('company', '')}",
        f"Signature:\n{profile.get('signature', '')}"
    ])

    messages = [
        {
            "role": "system",
            "content": (
                "You generate a professional reply to an incoming email.\n\n"

                "IMPORTANT FORMATTING RULE:\n"
                "• Do NOT bold entire sentences.\n"
                "• Do NOT overuse bolding.\n\n"


                "If placeholders like [Name], [Company], or [Signature] appear, "
                "replace them using the user profile below.\n\n"

                "USER PROFILE:\n"
                f"{profile_context}"
            )
        },
        {
            "role": "user",
            "content": f"Incoming Email\nSubject: {subject}\n\nBody:\n{body}"
        }
    ]

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=policy.temperature,
        max_completion_tokens=1024,
        stream=False
    )

    return completion.choices[0].message.content