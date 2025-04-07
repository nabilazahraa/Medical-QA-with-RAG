// const Hero = () => {
//   return (
//     <div
//       className="h-screen bg-cover bg-center flex flex-col justify-center items-center text-white text-center px-4"
//       style={{ backgroundImage: `url('/med.jpg')` }}
//     >
//       <h1 className="text-5xl font-bold mb-4">WELCOME TO<br />MEDGPT</h1>
//       <p className="text-lg max-w-xl mb-6">
//         Instant, AI-powered answers to your medical questions—leveraging AWS and BioBERT for real-time, accurate healthcare insights.
//       </p>
//       <a
//         href="#features"
//         className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-full transition duration-300"
//       >
//         TRY IT NOW!
//       </a>
//     </div>
//   );
// };

// export default Hero;

import { useNavigate } from 'react-router-dom';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <div
      className="h-screen bg-cover bg-center flex flex-col justify-center items-center text-white text-center px-4"
      style={{ backgroundImage: `url('/med.jpg')` }}
    >
      <h1 className="text-5xl font-bold mb-4">WELCOME TO<br />MEDGPT</h1>
      <p className="text-lg max-w-xl mb-6">
        Instant, AI-powered answers to your medical questions—leveraging AWS and BioBERT for real-time, accurate healthcare insights.
      </p>
      <button
        onClick={() => navigate("/search")}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-full transition duration-300"
      >
        TRY IT NOW!
      </button>
    </div>
  );
};

export default Hero;



