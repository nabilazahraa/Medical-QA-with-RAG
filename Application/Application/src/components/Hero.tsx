
import { useNavigate } from 'react-router-dom';

const Hero = () => {
  const navigate = useNavigate();

  return (
    <div className="relative h-screen w-full">
      {/* Background Image */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0"
        style={{
          backgroundImage: `url('/img.avif')`,
        }}
      />

      {/* Overlay */}
      <div className="absolute inset-0 bg-black opacity-60 z-10" />

      {/* Text Content Overlaid */}
      <div className="relative z-20 flex flex-col justify-center items-center h-full text-white text-center px-4 pt-16">
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
    </div>
  );
};

export default Hero;
