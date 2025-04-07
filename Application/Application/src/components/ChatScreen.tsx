

// import { useLocation, useNavigate } from "react-router-dom";
// import { useState } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState(() =>
//     initialQuery
//       ? [
//           { role: "user", text: initialQuery },
//           { role: "bot", text: "Loading answer..." },
//         ]
//       : []
//   );
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const sendQuestionToAPI = async (question: string) => {
//     setLoading(true);
//     try {
//       const res = await fetch("http://127.0.0.1:9000/ask", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ question }),
//       });

//       const data = await res.json();
//       return data.answer;
//     } catch (error) {
//       console.error("API error:", error);
//       return "Sorry, there was an error getting your answer.";
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSend = async () => {
//     if (!input.trim()) return;

//     const question = input.trim();

//     // Add user message to chat
//     setMessages((prev) => [...prev, { role: "user", text: question }]);
//     setInput("");

//     // Add a temporary loading message for the bot
//     setMessages((prev) => [...prev, { role: "bot", text: "Loading answer..." }]);

//     // Send question to API and await the answer
//     const answer = await sendQuestionToAPI(question);

//     // Replace the temporary loading message with the actual answer
//     setMessages((prev) => {
//       const updated = [...prev];
//       updated[updated.length - 1] = { role: "bot", text: answer };
//       return updated;
//     });
//   };

//   return (
//     <div
//       className="h-screen w-full bg-cover bg-center flex flex-col items-center justify-start pt-16 relative px-4"
//       style={{ backgroundImage: "url('/med.jpg')" }}
//     >
//       {/* Background overlay */}
//       <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

//       {/* Chat window */}
//       <div className="relative z-10 w-full max-w-5xl h-[60vh] bg-[#0e0f1af2] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
//         {/* Header */}
//         <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
//           MedGPT
//         </div>

//         {/* Chat messages */}
//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`max-w-[80%] px-4 py-3 rounded-xl text-sm sm:text-base ${
//                 msg.role === "user"
//                   ? "bg-blue-500 self-end text-white"
//                   : "bg-white/10 self-start text-white"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         {/* Input field and send button */}
//         <div className="p-4 border-t border-white/10 flex items-center gap-3 bg-black/40">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder="Ask another question..."
//             className="flex-1 bg-white/10 text-white rounded-full px-4 py-2 outline-none placeholder:text-gray-300"
//             onKeyDown={(e) => e.key === "Enter" && handleSend()}
//             disabled={loading}
//           />
//           <button
//             onClick={handleSend}
//             className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-full"
//             disabled={loading}
//           >
//             ➤
//           </button>
//         </div>
//       </div>

//       {/* Back Button */}
//       <button
//         onClick={() => navigate("/search")}
//         className="mt-6 bg-white text-black font-medium px-6 py-2 rounded-full shadow-lg hover:bg-gray-200 transition z-10"
//       >
//         ← Back
//       </button>
//     </div>
//   );
// };

// export default ChatScreen;


// import { useLocation, useNavigate } from "react-router-dom";
// import { useState, useEffect } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState(() =>
//     initialQuery
//       ? [{ role: "user", text: initialQuery }]
//       : []
//   );
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const sendQuestionToAPI = async (question: string) => {
//     setLoading(true);
//     try {
//       const res = await fetch("http://127.0.0.1:9000/ask", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ question }),
//       });
//       const data = await res.json();
//       return data.answer;
//     } catch (error) {
//       console.error("API error:", error);
//       return "Sorry, there was an error getting your answer.";
//     } finally {
//       setLoading(false);
//     }
//   };

//   const typeOutAnswer = (finalText: string) => {
//     let currentIndex = 0;
//     const interval = setInterval(() => {
//       currentIndex++;
//       setMessages((prev) => {
//         const newMessages = [...prev];
//         // Update the last message (bot's message) with substring of answer
//         newMessages[newMessages.length - 1] = {
//           role: "bot",
//           text: finalText.substring(0, currentIndex),
//         };
//         return newMessages;
//       });
//       if (currentIndex >= finalText.length) clearInterval(interval);
//     }, 50);
//   };

 
//   const handleSend = async () => {
//     if (!input.trim()) return;
//     const question = input.trim();
  
//     // Add user message
//     setMessages((prev) => [...prev, { role: "user", text: question }]);
//     setInput("");
  
//     // Add "Thinking..." placeholder before calling the API
//     setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);
  
//     const answer = await sendQuestionToAPI(question);
  
//     // Replace "Thinking..." with an empty bot message before typing
//     setMessages((prev) => {
//       const updated = [...prev];
//       updated[updated.length - 1] = { role: "bot", text: "" };
//       return updated;
//     });
  
//     typeOutAnswer(answer);
//   };
  
//   // On mount, if there's an initial query, send it automatically
//   useEffect(() => {
//     if (initialQuery) {
//       // Add empty bot answer placeholder if not already added
//       setMessages((prev) => [...prev, { role: "bot", text: "" }]);
//       (async () => {
//         const answer = await sendQuestionToAPI(initialQuery);
//         typeOutAnswer(answer);
//       })();
//     }
//   }, [initialQuery]);

//   return (
//     <div
//       className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
//       style={{ 
//         backgroundImage: `url('/bg.png')`,
//         paddingTop: "64px" // Adjust this value to match your header height
//       }}
//     >
//       <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

//       <div className="relative z-10 w-full max-w-5xl h-[80vh] bg-[#0e0f1af2] rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
//         <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
//           MedGPT
//         </div>

//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`max-w-[80%] px-4 py-3 rounded-xl text-sm sm:text-base ${
//                 msg.role === "user"
//                   ? "bg-sky-500 self-end text-white ml-auto"
//                   : "bg-white/10 self-start text-white mr-auto"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         <div className="p-4 border-t border-white/10 flex items-center gap-3 bg-black/40">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder={loading ? "Please wait..." : "Ask another question..."}
//             className="flex-1 bg-white/10 text-white rounded-full px-4 py-2 outline-none placeholder:text-gray-300"
//             onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
//             disabled={loading}
//           />
//           <button
//             onClick={handleSend}
//             className={`${loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-sky-500 hover:bg-sky-600'} px-4 py-2 rounded-full transition duration-300`}
//             disabled={loading}
//           >
//             {loading ? "..." : "➤"}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatScreen;

// import { useLocation, useNavigate } from "react-router-dom";
// import { useState, useEffect } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState(() =>
//     initialQuery
//       ? [{ role: "user", text: initialQuery }]
//       : []
//   );
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const sendQuestionToAPI = async (question: string) => {
//     setLoading(true);
//     try {
//       const res = await fetch("http://127.0.0.1:9000/ask", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ question }),
//       });
//       const data = await res.json();
//       return data.answer;
//     } catch (error) {
//       console.error("API error:", error);
//       return "Sorry, there was an error getting your answer.";
//     } finally {
//       setLoading(false);
//     }
//   };

//   const typeOutAnswer = (finalText: string) => {
//     let currentIndex = 0;
//     const interval = setInterval(() => {
//       currentIndex++;
//       setMessages((prev) => {
//         const newMessages = [...prev];
//         // Update the last message (bot's message) with substring of answer
//         newMessages[newMessages.length - 1] = {
//           role: "bot",
//           text: finalText.substring(0, currentIndex),
//         };
//         return newMessages;
//       });
//       if (currentIndex >= finalText.length) clearInterval(interval);
//     }, 50);
//   };

 
//   const handleSend = async () => {
//     if (!input.trim()) return;
//     const question = input.trim();
  
//     // Add user message
//     setMessages((prev) => [...prev, { role: "user", text: question }]);
//     setInput("");
  
//     // Add "Thinking..." placeholder before calling the API
//     setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);
  
//     const answer = await sendQuestionToAPI(question);
  
//     // Replace "Thinking..." with an empty bot message before typing
//     setMessages((prev) => {
//       const updated = [...prev];
//       updated[updated.length - 1] = { role: "bot", text: "" };
//       return updated;
//     });
  
//     typeOutAnswer(answer);
//   };
  
//   // On mount, if there's an initial query, send it automatically
//   useEffect(() => {
//     if (initialQuery) {
//       // Add empty bot answer placeholder if not already added
//       setMessages((prev) => [...prev, { role: "bot", text: "" }]);
//       (async () => {
//         const answer = await sendQuestionToAPI(initialQuery);
//         typeOutAnswer(answer);
//       })();
//     }
//   }, [initialQuery]);

//   return (
//     <div
//       className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
//       style={{ 
//         backgroundImage: `url('/bg.png')`,
//         paddingTop: "64px" // Adjust this value to match your header height
//       }}
//     >
//       <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

//       <div className="relative z-10 w-full max-w-5xl h-[80vh] bg-gray-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
//         <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
//           MedGPT
//         </div>

//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div
//               key={index}
//               className={`max-w-[80%] px-4 py-3 rounded-xl text-sm sm:text-base text-left ${
//                 msg.role === "user"
//                   ? "bg-sky-500 text-white ml-auto"
//                   : "bg-white/10 text-white mr-auto"
//               }`}
//             >
//               {msg.text}
//             </div>
//           ))}
//         </div>

//         <div className="p-4 border-t border-white/10 flex items-center gap-3 bg-black/40">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder={loading ? "Please wait..." : "Ask another question..."}
//             className="flex-1 bg-white/10 text-white rounded-full px-4 py-2 outline-none placeholder:text-gray-300"
//             onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
//             disabled={loading}
//           />
//           <button
//             onClick={handleSend}
//             className={`${loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-sky-500 hover:bg-sky-600'} px-4 py-2 rounded-full transition duration-300`}
//             disabled={loading}
//           >
//             {loading ? "..." : "➤"}
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ChatScreen;
import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

const ChatScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialQuery = (location.state as any)?.query || "";

  const [messages, setMessages] = useState(() =>
    initialQuery
      ? [{ role: "user", text: initialQuery }]
      : []
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendQuestionToAPI = async (question: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:9000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      return data.answer;
    } catch (error) {
      console.error("API error:", error);
      return "Sorry, there was an error getting your answer.";
    } finally {
      setLoading(false);
    }
  };

  const typeOutAnswer = (finalText: string) => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      currentIndex++;
      setMessages((prev) => {
        const newMessages = [...prev];
        // Update the last message (bot's message) with substring of answer
        newMessages[newMessages.length - 1] = {
          role: "bot",
          text: finalText.substring(0, currentIndex),
        };
        return newMessages;
      });
      if (currentIndex >= finalText.length) clearInterval(interval);
    }, 50);
  };

 
  const handleSend = async () => {
    if (!input.trim()) return;
    const question = input.trim();
  
    // Add user message
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
  
    // Add "Thinking..." placeholder before calling the API
    setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);
  
    const answer = await sendQuestionToAPI(question);
  
    // Replace "Thinking..." with an empty bot message before typing
    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = { role: "bot", text: "" };
      return updated;
    });
  
    typeOutAnswer(answer);
  };
  
  // On mount, if there's an initial query, send it automatically
  useEffect(() => {
    if (initialQuery) {
      // Add empty bot answer placeholder if not already added
      setMessages((prev) => [...prev, { role: "bot", text: "" }]);
      (async () => {
        const answer = await sendQuestionToAPI(initialQuery);
        typeOutAnswer(answer);
      })();
    }
  }, [initialQuery]);

  return (
    <div
      className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
      style={{ 
        backgroundImage: `url('/bg.png')`,
        paddingTop: "64px" // Adjust this value to match your header height
      }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

      <div className="relative z-10 w-full max-w-5xl h-[80vh] bg-gray-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
        <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
          MedGPT
        </div>

        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {messages.map((msg, index) => (
            <div className="flex w-full">
              <div
                key={index}
                className={`px-4 py-3 rounded-xl text-sm sm:text-base text-left ${
                  msg.role === "user"
                    ? "bg-sky-600 text-white ml-auto inline-block"
                    : "bg-white/10 text-white mr-auto inline-block"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-white/10 flex items-center gap-3 bg-black/40">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={loading ? "Please wait..." : "Ask another question..."}
            className="flex-1 bg-white/10 text-white rounded-full px-4 py-2 outline-none placeholder:text-gray-300"
            onKeyDown={(e) => e.key === "Enter" && !loading && handleSend()}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            className={`${loading ? 'bg-gray-500 cursor-not-allowed' : 'bg-sky-500 hover:bg-sky-600'} px-4 py-2 rounded-full transition duration-300`}
            disabled={loading}
          >
            {loading ? "..." : "➤"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;