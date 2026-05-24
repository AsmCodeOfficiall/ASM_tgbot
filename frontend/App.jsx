import { useCallback, useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "./api";
import Dashboard from "./components/Dashboard";
import ProjectModal from "./components/ProjectModal";
import SuccessToast from "./components/SuccessToast";
import TransactionList from "./components/TransactionList";
import OnboardingScreen from "./components/OnboardingScreen";
import { useTelegramTheme } from "./hooks/useTelegramTheme";
import { tg } from "./utils/theme";

const EMPTY_DATA = {fund: 0, balance: 0, transactions: [], hasTeam: null};

export default function App() {
  useTelegramTheme();

  //const [data, setData] = useState({ fund: 0, balance: 0, transactions: [], hasTeam: false });
  const [data, setData] = useState({EMPTY_DATA});
  const [isLoading, setIsLoading] = useState(true);   // true
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);


  const loadDashboard = useCallback(async () => {
    setError(null);
    try {
      const result = await fetchApi("/api/dashboard");
      setData({
        fund: result.fund ?? 0,
        balance: result.balance ?? 0,
        transactions: result.transactions ?? [],
        hasTeam: result.has_team ?? false,
      });
      return true;
    } catch (err) {
      console.error("Dashboard load failed:", err);
      setError(err.message || "Не вдалося завантажити дані");
      return false;
    }
  }, []);

  useEffect(() => {
    (async () => {
      setIsLoading(true);
      await loadDashboard();
      setIsLoading(false);
    })();
  }, [loadDashboard]);

  useEffect(() => {
    if (!successMessage) return undefined;
    const timer = setTimeout(() => setSuccessMessage(null), 3500);
    return () => clearTimeout(timer);
  }, [successMessage]);

  const handleOpenModal = () => {
    WebApp.HapticFeedback.impactOccurred("light");
    setIsModalOpen(true);
  };

  const handleCloseModal = () => setIsModalOpen(false);

  const handleProjectSuccess = async () => {
    await loadDashboard();
    setSuccessMessage("Проєкт успішно додано!");
  };

  const handleRetry = async () => {
    setIsLoading(true);
    await loadDashboard();
    setIsLoading(false);
  };

  const handleCreateTeam = async(teamData) => {
    setIsLoading(true);
    setError(null);
    try {
      //setData((prevData) => ({
      //  ...prevData,
      //  hasTeam: true
      //}));
      await fetchApi("api/team", {method: "POST", body: JSON.stringify(teamData)});
      await loadDashboard();
    } catch(err) {
      console.error("Помилка створення команди: ", err);
      setError(err.message || "Не вдалося створити команду");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div
      className="min-h-screen flex flex-col gap-3 p-4 pb-6"
      style={{
        backgroundColor: tg.bg,
        color: tg.text,
        paddingBottom: "calc(1.5rem + env(safe-area-inset-bottom, 0px))",
      }}
    >
      <SuccessToast message={successMessage} />

      {isLoading ? (
        <div className="flex flex-1 justify-center items-center min-h-[50vh]">
          <span style={{ color: tg.hint }}>Завантаження...</span>
        </div>
      ) : error ? (
        <div className="flex flex-1 flex-col justify-center items-center gap-4 min-h-[50vh] text-center p-4">
          <div className="text-5xl mb-2">⚠️</div>
          <p className="text-lg font-medium" style={{ color: tg.hint }}>{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            className="px-8 py-3 rounded-xl font-semibold mt-2 shadow-lg active:scale-95 transition-transform"
            style={{ backgroundColor: tg.button, color: tg.buttonText }}
          >
            Спробувати знову
          </button>
        </div>
      ) : data.hasTeam === false ? (
        <OnboardingScreen onCreateTeam = {handleCreateTeam} />
      ) : (
        <>
          <Dashboard fund={data.fund} balance={data.balance} />

          {!isModalOpen && (
            <button
              type="button"
              onClick={handleOpenModal}
              className="w-full font-semibold py-3 px-4 rounded-xl shrink-0"
              style={{ backgroundColor: tg.button, color: tg.buttonText }}
            >
              Додати проєкт
            </button>
          )}

          <TransactionList transactions={data.transactions} />
        </>
      )}

      {isModalOpen && (
        <ProjectModal
          onClose={handleCloseModal}
          onSuccess={handleProjectSuccess}
        />
      )}
    </div>
  );
}
