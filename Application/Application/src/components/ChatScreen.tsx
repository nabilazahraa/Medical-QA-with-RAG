
// import { useLocation, useNavigate } from "react-router-dom";
// import { useState, useEffect } from "react";

// const ChatScreen = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const initialQuery = (location.state as any)?.query || "";

//   const [messages, setMessages] = useState<{ role: string; text: string; timeTaken?: number }[]>(() =>
//     initialQuery ? [{ role: "user", text: initialQuery }] : []
//   );
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [isTyping, setIsTyping] = useState(false);

//   const sendQuestionToAPI = async (question: string) => {
//     setLoading(true);
//     try {
//       const res = await fetch("http://127.0.0.1:8000/ask", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ question }),
//       });
//       const data = await res.json();
//       return { answer: data.answer, timeTaken: data.time_taken };
//     } catch (error) {
//       console.error("API error:", error);
//       return { answer: "Sorry, there was an error getting your answer.", timeTaken: null };
//     } finally {
//       setLoading(false);
//     }
//   };

//   const typeOutAnswer = (finalText: string, onComplete: () => void) => {
//     let currentIndex = 0;
//     const interval = setInterval(() => {
//       currentIndex++;
//       setMessages((prev) => {
//         const newMessages = [...prev];
//         const lastMsg = newMessages[newMessages.length - 1];
//         newMessages[newMessages.length - 1] = {
//           role: "bot",
//           text: finalText.substring(0, currentIndex),
//         };
//         return newMessages;
//       });
//       if (currentIndex >= finalText.length) {
//         clearInterval(interval);
//         onComplete();  // invoke the callback after typing finishes
//       }
//     }, 20);
//   };
  

//   const handleSend = async () => {
//     if (!input.trim()) return;
//     const question = input.trim();
  
//     setMessages((prev) => [...prev, { role: "user", text: question }]);
//     setInput("");
  
//     setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);
//     setIsTyping(true);
  
//     const { answer, timeTaken } = await sendQuestionToAPI(question);
//     setIsTyping(false);
  
//     // Clear out placeholder text for bot
//     setMessages((prev) => {
//       const updated = [...prev];
//       updated[updated.length - 1] = { role: "bot", text: "" };
//       return updated;
//     });
  
//     // Type out the answer and once done, attach the timeTaken
//     typeOutAnswer(answer, () => {
//       setMessages((prev) => {
//         const updated = [...prev];
//         const last = updated[updated.length - 1];
//         updated[updated.length - 1] = { ...last, timeTaken };
//         return updated;
//       });
//     });
//   };
  

//   return (
//     <div
//       className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
//       style={{
//         backgroundImage: `url('/img.avif')`,
//         paddingTop: "64px",
//       }}
//     >
//       <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

//       <div className="relative z-10 w-full max-w-5xl h-[80vh] bg-gray-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
//         <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
//           MedGPT
//         </div>

//         <div className="flex-1 p-4 space-y-4 overflow-y-auto">
//           {messages.map((msg, index) => (
//             <div className="flex w-full" key={index}>
//               <div
//                 className={`px-4 py-3 rounded-xl text-sm sm:text-base text-left ${
//                   msg.role === "user"
//                     ? "bg-sky-600 text-white ml-auto inline-block"
//                     : "bg-white/10 text-white mr-auto inline-block"
//                 }`}
//               >
//                 <div>{msg.text}</div>
//                 {msg.role === "bot" && msg.timeTaken !== undefined && (
//                   <div className="mt-1 text-xs text-gray-400">
//                     Response time: {msg.timeTaken}s
//                   </div>
//                 )}
//               </div>
//             </div>
//           ))}
//           {isTyping && (
//             <div className="text-left text-sm text-gray-500 animate-pulse px-4">
//               MedGPT is thinking...
//             </div>
//           )}
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
//             className={`${
//               loading ? "bg-gray-500 cursor-not-allowed" : "bg-sky-500 hover:bg-sky-600"
//             } px-4 py-2 rounded-full transition duration-300`}
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
import { useState, useEffect, useRef } from "react";

const ChatScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const initialQuery = (location.state as any)?.query || "";

  const [messages, setMessages] = useState<{ role: string; text: string; timeTaken?: number }[]>(() =>
    initialQuery ? [{ role: "user", text: initialQuery }] : []
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendQuestionToAPI = async (question: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      return { answer: data.answer, timeTaken: data.time_taken };
    } catch (error) {
      console.error("API error:", error);
      return { answer: "Sorry, there was an error getting your answer.", timeTaken: null };
    } finally {
      setLoading(false);
    }
  };

  const typeOutAnswer = (finalText: string, onComplete: () => void) => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      currentIndex++;
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastMsg = newMessages[newMessages.length - 1];
        newMessages[newMessages.length - 1] = {
          role: "bot",
          text: finalText.substring(0, currentIndex),
        };
        return newMessages;
      });
      if (currentIndex >= finalText.length) {
        clearInterval(interval);
        onComplete();
      }
    }, 20);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const question = input.trim();

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");

    setMessages((prev) => [...prev, { role: "bot", text: "Thinking..." }]);
    setIsTyping(true);

    const { answer, timeTaken } = await sendQuestionToAPI(question);
    setIsTyping(false);

    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = { role: "bot", text: "" };
      return updated;
    });

    typeOutAnswer(answer, () => {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        updated[updated.length - 1] = { ...last, timeTaken };
        return updated;
      });
    });
  };

  return (
    <div
      className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
      style={{
        backgroundImage: `url('/img.avif')`,
        paddingTop: "64px",
      }}
    >
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-0" />

      <div className="relative z-10 w-full max-w-5xl h-[80vh] bg-gray-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-white/10">
        <div className="p-4 border-b border-white/10 text-xl font-semibold text-white bg-black/80 rounded-t-2xl">
          MedGPT
        </div>

        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          {messages.map((msg, index) => (
            <div className="flex w-full" key={index}>
              <div
                className={`px-4 py-3 rounded-xl text-sm sm:text-base text-left ${
                  msg.role === "user"
                    ? "bg-sky-600 text-white ml-auto inline-block"
                    : "bg-white/10 text-white mr-auto inline-block"
                }`}
              >
                <div>{msg.text}</div>
                {msg.role === "bot" && msg.timeTaken !== undefined && (
                  <div className="mt-1 text-xs text-gray-400">
                    Response time: {msg.timeTaken}s
                  </div>
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="text-left text-sm text-gray-500 animate-pulse px-4">
              MedGPT is thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
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
            className={`${
              loading ? "bg-gray-500 cursor-not-allowed" : "bg-sky-500 hover:bg-sky-600"
            } px-4 py-2 rounded-full transition duration-300`}
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
