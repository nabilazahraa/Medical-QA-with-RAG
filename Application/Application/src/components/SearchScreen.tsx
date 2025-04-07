


// import { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import { FaSearch, FaArrowRight } from "react-icons/fa";


// const SearchScreen = () => {
//   const [query, setQuery] = useState("");
//   const navigate = useNavigate();

//   const handleSubmit = () => {
//     if (query.trim()) {
//       navigate("/chat", { state: { query } });
//     }
//   };

//   return (
//     <div
//       className="h-screen bg-cover bg-center flex items-center justify-center"
//       style={{ backgroundImage: "url('/med.jpg')" }}
//     >
//       <div className="bg-white p-10 rounded-2xl shadow-2xl w-11/12 max-w-2xl text-center">
//         <h1 className="text-3xl font-bold mb-8">
//           Search <span className="text-black">MedGPT</span>
//         </h1>

//         <div className="flex items-center bg-gray-100 rounded-2xl px-6 py-4 space-x-4">
//           <FaSearch className="text-gray-500 text-xl" />
//           <input
//             type="text"
//             placeholder="What are you looking for?"
//             className="flex-1 bg-transparent outline-none text-gray-700 text-lg"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
//           />
//           <FaArrowRight
//             className="text-gray-500 text-xl cursor-pointer hover:text-blue-600"
//             onClick={handleSubmit}
//           />
//         </div>
//       </div>
//     </div>
//   );
// };

// export default SearchScreen;


import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaArrowRight } from "react-icons/fa";

const SearchScreen = () => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (query.trim()) {
      // Navigate to chat screen with the query in state
      navigate("/chat", { state: { query: query.trim() } });
    }
  };

  return (
    <div
      className="h-screen bg-cover bg-center flex items-center justify-center"
      style={{ backgroundImage: "url('/med.jpg')" }}
    >
      <div className="bg-white p-10 rounded-2xl shadow-2xl w-11/12 max-w-2xl text-center">
        <h1 className="text-3xl font-bold mb-8">
          Search <span className="text-black">MedGPT</span>
        </h1>

        <div className="flex items-center bg-gray-100 rounded-2xl px-6 py-4 space-x-4">
          <FaSearch className="text-gray-500 text-xl" />
          <input
            type="text"
            placeholder="What are you looking for?"
            className="flex-1 bg-transparent outline-none text-gray-700 text-lg"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />
          <FaArrowRight
            className="text-gray-500 text-xl cursor-pointer hover:text-blue-600"
            onClick={handleSubmit}
          />
        </div>
      </div>
 </div>

  );
};

export default SearchScreen;
