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
//       className="h-screen w-full bg-cover bg-center flex flex-col items-center justify-start pt-16 px-4"
//       style={{ backgroundImage: "url('/med.jpg')" }}
//     >
//       {/* Chat window */}
//       <div className="relative z-10 w-full max-w-4xl h-[60vh] bg-white rounded-2xl shadow-xl flex flex-col overflow-hidden border border-gray-200">
//         {/* Header */}
//         <div className="p-4 border-b border-gray-200 text-xl font-semibold text-black bg-white rounded-t-2xl">
//           MedGPT
//         </div>

//         {/* Messages */}
//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`w-full px-4 py-3 rounded-xl text-sm sm:text-base ${
//                 msg.role === "user"
//                   ? "bg-[#045F74] text-white text-right"
//                   : "bg-gray-100 text-gray-800 text-left shadow-sm"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         {/* Input */}
//         <div className="p-4 border-t border-gray-200 flex items-center gap-3 bg-white">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder="Ask another question..."
//             className="flex-1 bg-gray-100 text-black rounded-full px-4 py-2 outline-none placeholder:text-gray-500"
//           />
//           <button
//             onClick={handleSend}
//             className="bg-[#045F74] hover:bg-[#03495a] text-white px-4 py-2 rounded-full"
//           >
//             ➤
//           </button>
//         </div>
//       </div>

//       {/* Back Button */}
//       <button
//         onClick={() => navigate("/search")}
//         className="mt-6 bg-white text-black font-medium px-6 py-2 rounded-full shadow-md hover:bg-gray-200 transition z-10"
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
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: input }]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Dummy response to: " + input }
      ]);
      setIsTyping(false);
    }, 1000);
  };

  return (
    <div
      className="h-screen w-full bg-cover bg-center flex flex-col items-center justify-start pt-16 px-4 relative"
      style={{ backgroundImage: "url('/med.jpg')" }}
    >
      {/* Optional faint overlay for readability
      <div className="absolute inset-0 bg-white/10 backdrop-blur-sm z-0" /> */}

      {/* Chat window with glass blur */}
      <div className="relative z-10 w-full max-w-4xl min-h-[60vh] backdrop-blur-lg bg-white/90 shadow-2xl rounded-2xl flex flex-col overflow-hidden border border-gray-200">
        
        {/* Header */}
        <div className="p-4 border-b border-gray-200 text-xl font-semibold text-black bg-transparent">
          Your Chat
        </div>

        {/* Messages */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`w-full px-4 py-3 text-sm sm:text-base ${
                msg.role === "user"
                  ? "bg-[#045F74] text-white text-right rounded-l-2xl rounded-tr-2xl"
                  : "bg-gray-100 text-gray-800 text-left rounded-r-2xl rounded-tl-2xl shadow-sm"
              }`}
            >
              {msg.text}
            </div>
          ))}
          {isTyping && (
            <div className="text-left text-sm text-gray-500 animate-pulse px-4">
              MedGPT is typing...
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 flex items-center gap-3 bg-transparent">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask another question..."
            className="flex-1 bg-gray-100 text-black rounded-full px-4 py-2 outline-none placeholder:text-gray-500"
          />
          <button
            onClick={handleSend}
            className="bg-[#045F74] hover:bg-[#03495a] text-white px-4 py-2 rounded-full transition duration-300 ease-in-out transform hover:scale-105"
          >
            ➤
          </button>
        </div>
      </div>

      {/* Back Button */}
      <button
        onClick={() => navigate("/search")}
        className="mt-6 bg-white text-black font-medium px-6 py-2 rounded-full shadow-md hover:bg-gray-200 transition z-10"
      >
        ← Back
      </button>
    </div>
  );
};

export default ChatScreen;

