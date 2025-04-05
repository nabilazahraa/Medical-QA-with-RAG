// import { Routes, Route } from "react-router-dom";
// import Hero from "./components/Hero";
// import SearchScreen from "./components/SearchScreen";

// function App() {
//   return (
//     <div>
//       {/* 🔲 Navbar shown on all pages */}
//       <header className="flex justify-between items-center px-6 py-4 shadow-md bg-black fixed top-0 left-0 right-0 z-50">
//         <h1 className="text-xl font-bold text-white">MEDGPT</h1>
//         <nav className="space-x-6 text-white">
//           <a href="#features" className="hover:underline">FEATURES</a>
//           <a href="#about" className="hover:underline">ABOUT</a>
//         </nav>
//       </header>

//       {/* 🧠 Route content below navbar */}
//       <main className="pt-20">
//         <Routes>
//           <Route path="/" element={<Hero />} />
//           <Route path="/search" element={<SearchScreen />} />
//         </Routes>
//       </main>
//     </div>
//   );
// }

// export default App;


import { Routes, Route } from "react-router-dom";
import Hero from "./components/Hero";
import SearchScreen from "./components/SearchScreen";
import ChatScreen from "./components/ChatScreen";

function App() {
  return (
    <div>
      <header className="flex justify-between items-center px-6 py-4 shadow-md bg-black fixed top-0 left-0 right-0 z-50">
        <h1 className="text-xl font-bold text-white">MEDGPT</h1>
        <nav className="space-x-6 text-white">
          <a href="#features" className="hover:underline">FEATURES</a>
          <a href="#about" className="hover:underline">ABOUT</a>
        </nav>
      </header>

      <main className="pt-20">
        <Routes>
          <Route path="/" element={<Hero />} />
          <Route path="/search" element={<SearchScreen />} />
          <Route path="/chat" element={<ChatScreen />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;


