from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import EmailInput, FinalEmail
from app.groq_client import generate_reply
from app.rewards import compute_reward
from app.policy import policy
from app.schemas import UserProfile
from app.memory import set_user_profile, get_user_profile


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
def generate_email(data: EmailInput):
    draft = generate_reply(data.subject, data.body, data.user_id)
    return {"draft": draft, "temperature": policy.temperature}

@app.post("/finalize")
def finalize_email(data: FinalEmail):
    reward, metrics = compute_reward(data.draft, data.final)
    policy.update(reward)

    print("\n" + "=" * 60)
    print("📊 EMAIL EVALUATION METRICS")
    print("=" * 60)
    print(f"Normalized Edit Distance : {metrics['normalized_edit_distance']:.4f}")
    print(f"Zero Edit Acceptance     : {metrics['zero_edit']}")
    print(f"Flesch-Kincaid Grade     : {metrics['fk_grade']:.2f}")
    print(f"Readability (6–9)        : {metrics['readability_ok']}")
    print("-" * 60)
    print(f"Final Reward             : {reward:.4f}")
    print(f"Updated Temperature      : {policy.temperature:.2f}")
    print("=" * 60)

    return {
        "reward": reward,
        "temperature": policy.temperature
    }


@app.post("/profile")
def save_profile(profile: UserProfile):
    set_user_profile(profile.user_id, {
        "name": profile.name,
        "designation": profile.designation,
        "company": profile.company,
        "signature": profile.signature
    })
    return {"status": "Profile saved"}
