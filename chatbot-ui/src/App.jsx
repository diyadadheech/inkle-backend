import React, { useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", text: input }];
    setMessages(newMessages);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      const data = await response.json();

      setMessages([
        ...newMessages,
        {
          role: "bot",
          text:
            data.reply ||
            data.response ||
            "Sorry, no reply received.",
        },
      ]);
    } catch (error) {
      setMessages([
        ...newMessages,
        {
          role: "bot",
          text: "Error connecting to server.",
        },
      ]);
    }

    setInput("");
  };

  return (
    <div
      className="h-screen w-full bg-cover bg-center flex items-center justify-center p-4"
      style={{ backgroundImage: "url('/travel.jpg')" }}
    >
      <div className="w-full max-w-lg backdrop-blur-xl bg-white/30 shadow-xl rounded-2xl p-4 border border-white/40 flex flex-col">
        
        <h1 className="text-2xl font-bold text-center text-white drop-shadow mb-4">
          Inkle Travel Chatbot
        </h1>

        <div className="flex-1 overflow-y-auto p-3 border rounded-lg bg-white/60 backdrop-blur-md">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`my-2 p-2 rounded-lg max-w-[75%] whitespace-pre-line ${
                msg.role === "user"
                  ? "ml-auto bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 border p-2 rounded-lg bg-white/70 backdrop-blur-md"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            onClick={sendMessage}
            className="px-4 py-2 bg-blue-700 text-white rounded-lg shadow"
          >
            Send
          </button>
        </div>

      </div>
    </div>
  );
}

export default App;
