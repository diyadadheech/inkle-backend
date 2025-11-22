import React, { useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const newMessages = [...messages, { role: "user", text: input }];
    setMessages(newMessages);

    // Send to FastAPI backend
    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
      });

      const data = await response.json();

      // Add bot reply
      setMessages([...newMessages, { role: "bot", text: data.response }]);
    } catch (error) {
      setMessages([
        ...newMessages,
        { role: "bot", text: "Error connecting to server." },
      ]);
    }

    setInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-lg bg-white shadow-xl rounded-xl p-4 flex flex-col">
        
        {/* Header */}
        <h1 className="text-2xl font-bold text-center mb-4">Inkle Travel Chatbot</h1>

        {/* Chat Box */}
        <div className="flex-1 overflow-y-auto border rounded-lg p-3 bg-gray-50">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`my-2 p-2 rounded-lg w-fit max-w-[80%] ${
                msg.role === "user"
                  ? "bg-blue-500 text-white ml-auto"
                  : "bg-gray-300 text-black"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 p-2 border rounded-lg"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button
            onClick={sendMessage}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Send
          </button>
        </div>

      </div>
    </div>
  );
}

export default App;
