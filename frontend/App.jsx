import { useCallback, useEffect, useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "./api";
import Dashboard from "./components/Dashboard";
import ProjectModal from "./components/ProjectModal";
import SuccessToast from "./components/SuccessToast";
import OnboardingScreen from "./components/OnboardingScreen";
import { useTelegramTheme } from "./hooks/useTelegramTheme";
import { tg } from "./utils/theme";

export default function App() {
  useTelegramTheme();

  const [data, setData] = useState({ 
    fund: 0, 
    balance: 0, 
    transactions: [], 
    hasTeam: null,
    inviteCode: "",
    teamName: "",
    role: "user",
    tax: 10,
    projects: [],
    members: []
  });

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
        hasTeam: result.has_team ?? false,
        teamName: result.team_name ?? "Без назви",
        inviteCode: result.team?.invite_code ?? "",
        role: result.role ?? "user",
        tax: result.tax ?? 10,
        projects: result.projects ?? [],
        members: result.members ?? []
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

  const handleFinishOnboarding = async () => {
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
        <OnboardingScreen onFinish={handleFinishOnboarding} />
      ) : (
        <>
          <Dashboard 
            fund={data.fund} 
            balance={data.balance} 
            teamName={data.teamName}
            role={role}          
            tax={data.tax}            
            projects={data.projects}
            transactions={data.transactions}
            inviteCode={data.inviteCode}
            members={data.members}
            onAddProject={handleOpenModal}
          />
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