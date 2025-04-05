// import { useLocation } from "react-router-dom";
// import { useState } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState([
//     { role: "user", text: initialQuery },
//     { role: "bot", text: "This is a dummy reply for now. Your RAG model will generate the real one." },
//   ]);
//   const [input, setInput] = useState("");

//   const handleSend = () => {
//     if (!input.trim()) return;

//     setMessages((prev) => [
//       ...prev,
//       { role: "user", text: input },
//       { role: "bot", text: "Dummy response to: " + input },
//     ]);
//     setInput("");
//   };

//   return (
//     <div className="h-screen bg-gray-900 text-white flex items-center justify-center px-4">
//       <div className="w-full max-w-3xl h-[85vh] bg-[#0e0f1a] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
//         {/* Header */}
//         <div className="p-4 border-b border-gray-700 text-xl font-bold bg-black">
//           MedGPT
//         </div>

//         {/* Messages */}
//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`max-w-[70%] p-3 rounded-xl ${
//                 msg.role === "user"
//                   ? "bg-blue-600 self-end text-white"
//                   : "bg-gray-800 self-start text-gray-200"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         {/* Input */}
//         <div className="p-4 border-t border-gray-700 flex items-center gap-3 bg-[#0e0f1a]">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder="Ask another question..."
//             className="flex-1 bg-gray-800 text-white rounded-full px-4 py-2 outline-none"
//           />
//           <button
//             onClick={handleSend}
//             className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-full"
//           >
//             ➤
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatScreen;


// import { useLocation, useNavigate } from "react-router-dom";
// import { useState } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState([
//     { role: "user", text: initialQuery },
//     { role: "bot", text: "This is a dummy reply for now. Your RAG model will generate the real one." },
//   ]);
//   const [input, setInput] = useState("");

//   const handleSend = () => {
//     if (!input.trim()) return;
//     setMessages((prev) => [
//       ...prev,
//       { role: "user", text: input },
//       { role: "bot", text: "Dummy response to: " + input },
//     ]);
//     setInput("");
//   };

//   return (
//     <div
//       className="h-screen w-full bg-cover bg-center flex flex-col items-center justify-center px-4"
//       style={{ backgroundImage: "url('/med.jpg')" }} // your image from /public
//     >
//       <div className="w-full max-w-3xl h-[85vh] bg-[#0e0f1a] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
//         {/* Header */}
//         <div className="p-4 border-b border-gray-700 text-xl font-bold bg-black">
//           MedGPT
//         </div>

//         {/* Messages */}
//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`max-w-[70%] p-3 rounded-xl ${
//                 msg.role === "user"
//                   ? "bg-blue-600 self-end text-white"
//                   : "bg-gray-800 self-start text-gray-200"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         {/* Input */}
//         <div className="p-4 border-t border-gray-700 flex items-center gap-3 bg-[#0e0f1a]">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder="Ask another question..."
//             className="flex-1 bg-gray-800 text-white rounded-full px-4 py-2 outline-none"
//           />
//           <button
//             onClick={handleSend}
//             className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-full"
//           >
//             ➤
//           </button>
//         </div>
//       </div>

//       {/* Back Button */}
//       <button
//         onClick={() => navigate("/search")}
//         className="mt-6 bg-white text-black font-semibold px-6 py-2 rounded-full shadow hover:bg-gray-200 transition"
//       >
//         ← Back
//       </button>
//     </div>
//   );
// };

// export default ChatScreen;

import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";

const ChatScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialQuery = (location.state as any)?.query || "";

  const [messages, setMessages] = useState([
    { role: "user", text: initialQuery },
    { role: "bot", text: "This is a dummy reply for now. Your RAG model will generate the real one." },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { role: "user", text: input },
      { role: "bot", text: "Dummy response to: " + input },
    ]);
    setInput("");
  };

  return (
    <div
      className="h-screen w-full bg-cover bg-center flex flex-col items-center justify-start pt-16 relative px-4"
      style={{ backgroundImage: "url('/med.jpg')" }}
    >
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

      {/* Chat Window */}
      <div className="relative z-10 w-full max-w-5xl h-[60vh] bg-[#0e0f1af2] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
        
        {/* Header */}
        <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
          MedGPT
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`max-w-[80%] px-4 py-3 rounded-xl text-sm sm:text-base ${
                msg.role === "user"
                  ? "bg-blue-500 self-end text-white"
                  : "bg-white/10 self-start text-white"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/10 flex items-center gap-3 bg-black/40">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask another question..."
            className="flex-1 bg-white/10 text-white rounded-full px-4 py-2 outline-none placeholder:text-gray-300"
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-full"
          >
            ➤
          </button>
        </div>
      </div>

      {/* Back Button */}
      <button
        onClick={() => navigate("/search")}
        className="mt-6 bg-white text-black font-medium px-6 py-2 rounded-full shadow-lg hover:bg-gray-200 transition z-10"
      >
        ← Back
      </button>
    </div>
  );
};

export default ChatScreen;
