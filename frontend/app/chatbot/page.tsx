"use client";

import { useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatbotPage() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I can analyze the landslide risk using the terrain and satellite data available in the backend. Ask me about landslide risk, terrain, slope, vegetation, or a specific location.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message.trim();

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          history: messages,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the backend. Make sure the FastAPI server is running on port 8000.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "40px",
      }}
    >
      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          background: "white",
          borderRadius: "16px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            background: "#111827",
            color: "white",
            padding: "24px",
          }}
        >
          <h1 style={{ margin: 0 }}>Landslide Risk Assistant</h1>
          <p style={{ margin: "8px 0 0", color: "#d1d5db" }}>
            AI-powered analysis of terrain and satellite data
          </p>
        </div>

        <div
          style={{
            height: "500px",
            overflowY: "auto",
            padding: "24px",
          }}
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent:
                  msg.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "16px",
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: "14px 18px",
                  borderRadius: "12px",
                  background:
                    msg.role === "user" ? "#2563eb" : "#f3f4f6",
                  color: msg.role === "user" ? "white" : "#111827",
                  whiteSpace: "pre-wrap",
                  lineHeight: "1.5",
                }}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div
              style={{
                color: "#6b7280",
                padding: "10px",
              }}
            >
              Analyzing terrain data...
            </div>
          )}
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            padding: "20px",
            borderTop: "1px solid #e5e7eb",
          }}
        >
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
            placeholder="Ask about landslide risk..."
            style={{
              flex: 1,
              padding: "14px",
              border: "1px solid #d1d5db",
              borderRadius: "10px",
              fontSize: "16px",
              outline: "none",
            }}
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            style={{
              padding: "14px 24px",
              border: "none",
              borderRadius: "10px",
              background: loading ? "#9ca3af" : "#2563eb",
              color: "white",
              fontSize: "16px",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Analyzing..." : "Send"}
          </button>
        </div>
      </div>
    </main>
  );
}