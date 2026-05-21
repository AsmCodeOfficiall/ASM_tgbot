import { useCallback, useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "./api";
import Dashboard from "./components/Dashboard";
import ProjectModal from "./components/ProjectModal";
import SuccessToast from "./components/SuccessToast";
import TransactionList from "./components/TransactionList";
import { useTelegramTheme } from "./hooks/useTelegramTheme";
import { tg } from "./utils/theme";

const EMPTY_DATA = { fund: 0, balance: 0, transactions: [] };

export default function App() {
  useTelegramTheme();

  const [data, setData] = useState(EMPTY_DATA);
  const [isLoading, setIsLoading] = useState(true);
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
        <div className="flex flex-1 flex-col justify-center items-center gap-4 min-h-[50vh] text-center">
          <p style={{ color: tg.hint }}>{error}</p>
          <button
            type="button"
            onClick={handleRetry}
            className="px-6 py-3 rounded-xl font-semibold"
            style={{ backgroundColor: tg.button, color: tg.buttonText }}
          >
            Спробувати знову
          </button>
        </div>
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
