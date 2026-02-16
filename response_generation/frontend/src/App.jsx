import React, { useState } from "react";
import { generateEmail, finalizeEmail, saveProfile } from "./api";

export default function App() {
  // Email states
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [draft, setDraft] = useState("");
  const [finalText, setFinalText] = useState("");
  const [reward, setReward] = useState(null);
  const [loading, setLoading] = useState(false);

  // User profile (memory)
  const [profile, setProfile] = useState({
    name: "",
    designation: "",
    company: "",
    signature: ""
  });

  // Save user profile to backend
  const handleSaveProfile = async () => {
    if (!profile.name) {
      alert("Please enter at least your name");
      return;
    }

    await saveProfile({
      user_id: "user1",
      ...profile
    });

    alert("Profile saved successfully");
  };

  // Generate reply
  const handleGenerate = async () => {
    if (!subject || !body) {
      alert("Please enter subject and body");
      return;
    }

    setLoading(true);
    const res = await generateEmail(subject, body);
    setDraft(res.draft);
    setFinalText(res.draft);
    setReward(null);
    setLoading(false);
  };

  // Finalize and send for evaluation
  const handleFinalize = async () => {
    setLoading(true);
    const res = await finalizeEmail(draft, finalText);
    setReward(res.reward);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: 20 }}>
      <h2>RL Email Assistant</h2>

      {/* ================= USER PROFILE ================= */}
      <h3>User Profile (Memory)</h3>

      <input
        placeholder="Your Name"
        value={profile.name}
        onChange={e => setProfile({ ...profile, name: e.target.value })}
        style={{ width: "100%", marginBottom: 8 }}
      />

      <input
        placeholder="Designation"
        value={profile.designation}
        onChange={e => setProfile({ ...profile, designation: e.target.value })}
        style={{ width: "100%", marginBottom: 8 }}
      />

      <input
        placeholder="Company"
        value={profile.company}
        onChange={e => setProfile({ ...profile, company: e.target.value })}
        style={{ width: "100%", marginBottom: 8 }}
      />

      <textarea
        placeholder="Email Signature"
        rows={3}
        value={profile.signature}
        onChange={e => setProfile({ ...profile, signature: e.target.value })}
        style={{ width: "100%", marginBottom: 10 }}
      />

      <button onClick={handleSaveProfile}>
        Save Profile
      </button>

      <hr style={{ margin: "20px 0" }} />

      {/* ================= EMAIL INPUT ================= */}
      <label>Incoming Email Subject</label>
      <input
        type="text"
        value={subject}
        onChange={e => setSubject(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
      />

      <label>Incoming Email Body</label>
      <textarea
        rows={6}
        value={body}
        onChange={e => setBody(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
      />

      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate Reply"}
      </button>

      {/* ================= EDIT GENERATED REPLY ================= */}
      {draft && (
        <>
          <h3 style={{ marginTop: 20 }}>Edit Generated Reply</h3>

          <textarea
            rows={10}
            value={finalText}
            onChange={e => setFinalText(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />

          <button onClick={handleFinalize} disabled={loading}>
            {loading ? "Finalizing..." : "FINAL"}
          </button>
        </>
      )}

      {/* ================= REWARD ================= */}
      {reward !== null && (
        <p style={{ marginTop: 20 }}>
          <strong>Reward:</strong> {reward.toFixed(3)}
        </p>
      )}
    </div>
  );
}
