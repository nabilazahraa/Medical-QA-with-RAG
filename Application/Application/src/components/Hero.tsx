

// import { useNavigate } from 'react-router-dom';

// const Hero = () => {
//   const navigate = useNavigate();

//   return (
//     <div
//       className="h-screen bg-cover bg-center flex flex-col justify-center items-center text-white text-center px-4"
//       style={{ backgroundImage: `url('/bg.png')` }}
//     >
//       <h1 className="text-5xl font-bold mb-4">WELCOME TO<br />MEDGPT</h1>
//       <p className="text-lg max-w-xl mb-6">
//         Instant, AI-powered answers to your medical questions.
//       </p>
//       <button
//         onClick={() => navigate("/chat")}
//         className="bg-sky-500 hover:bg-sky-600 text-white font-semibold py-2 px-6 rounded-full transition duration-300"
//       >
//         START NOW!
//       </button>
//     </div>
//   );
// };

// export default Hero;

// import { useNavigate } from 'react-router-dom';

// const Hero = () => {
//   const navigate = useNavigate();

//   return (
//     <div
//       className="h-screen bg-cover bg-center bg-fixed flex flex-col justify-center items-center text-white text-center px-4"
//       style={{ 
//         backgroundImage: `url('/bg.png')`,
//         // marginTop: 0,
//         paddingTop: "64px" // Adjust this value to match your header height
//       }}
//     >
//       <h1 className="text-5xl font-bold mb-4">WELCOME TO<br />MEDGPT</h1>
//       <p className="text-lg max-w-xl mb-6">
//         Instant, AI-powered answers to your medical questions.
//       </p>
//       <button
//         onClick={() => navigate("/chat")}
//         className="bg-sky-500 hover:bg-sky-600 text-white font-semibold py-2 px-6 rounded-full transition duration-300"
//       >
//         START NOW!
//       </button>
//     </div>
//   );
// };

// export default Hero;
import { useNavigate } from 'react-router-dom';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <div
      className="fixed inset-0 bg-cover bg-center bg-no-repeat flex flex-col justify-center items-center text-white text-center px-4"
      style={{ 
        backgroundImage: `url('/bg.png')`,
        paddingTop: "64px" // Adjust this value to match your header height
      }}
    >
      <h1 className="text-5xl font-bold mb-4">WELCOME TO<br />MEDGPT</h1>
      <p className="text-lg max-w-xl mb-6">
        Instant, AI-powered answers to your medical questions.
      </p>
      <button
        onClick={() => navigate("/chat")}
        className="bg-sky-500 hover:bg-sky-600 text-white font-semibold py-2 px-6 rounded-full transition duration-300"
      >
        START NOW!
      </button>
    </div>
  );
};

export default Hero;