const BACKEND_URL = "http://localhost:8000";

export async function generateEmail(subject, body) {
  const response = await fetch(`${BACKEND_URL}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      subject,
      body,
      user_id: "user1"
    })
  });

  return response.json();
}

export async function saveProfile(profile) {
  const res = await fetch("http://localhost:8000/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile)
  });
  return res.json();
}

export async function finalizeEmail(draft, finalText) {
  const response = await fetch(`${BACKEND_URL}/finalize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      draft,
      final: finalText,
      user_id: "user1"
    })
  });

  return response.json();
}
