import { tg } from "../utils/theme";

const SuccessToast = ({ message }) => {
  if (!message) return null;

  return (
    <div
      className="fixed top-4 left-4 right-4 z-[60] px-4 py-3 rounded-xl shadow-lg text-center text-sm font-medium animate-pulse"
      style={{
        backgroundColor: tg.button,
        color: tg.buttonText,
      }}
      role="status"
    >
      {message}
    </div>
  );
};

export default SuccessToast;
