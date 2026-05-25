import { useState } from "react";
import { formatUsd } from "../utils/format";
import { tg } from "../utils/theme";
import TransactionList from "./TransactionList";
import Settingsboard from "./Settingsboard";

const Dashboard = ({ fund, balance, teamName, role, transactions, projects = [], tax, members = [], inviteCode, onAddProject }) => {
  
  const [activeTab, setActiveTab] = useState("projects");
  const [expandedProjectId, setExpandedProjectId] = useState(null);
  const [showSettings, setShowSettings] = useState(false);


  if (showSettings) {
    return (
      <Settingsboard 
        role={role}
        onBack={() => setShowSettings(false)} 
        teamName={teamName}
        tax={tax}       
        members={members} 
        inviteCode={inviteCode}
        onRefresh={onAddProject} 
      />
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-between items-center px-1 mb-1">
        <div>
          <h1 className="text-2xl font-bold">{teamName || "Без назви"}</h1>
          <p className="text-xs font-medium mt-0.5" style={{ color: tg.hint }}>
            {role === "team_lead" ? "👑 Тімлід" : "💻 Розробник"}
          </p>
        </div>

        <button
          onClick={() => setShowSettings(true)}
          className="p-3 bg-neutral-800 rounded-full active:scale-95 transition-transform shadow-sm"
          style={{ backgroundColor: tg.secondaryBg, color: tg.text }}
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>

      <section className="p-5 rounded-2xl" style={{ backgroundColor: tg.secondaryBg }}>
        <h2 className="text-sm font-medium" style={{ color: tg.hint }}>Загальний фонд команди</h2>
        <p className="text-3xl font-bold mt-1 tabular-nums">{formatUsd(fund)}</p>
      </section>

      <section className="p-5 rounded-2xl" style={{ backgroundColor: tg.sectionBg, border: `1px solid ${tg.hint}` }}>
        <h2 className="text-sm font-medium" style={{ color: tg.link }}>Особистий баланс</h2>
        <p className="text-3xl font-bold mt-1 tabular-nums" style={{ color: tg.accent }}>{formatUsd(balance)}</p>
      </section>

      {role === "team_lead" && (
        <button
          type="button"
          onClick={onAddProject}
          className="w-full font-semibold py-3 px-4 rounded-xl active:scale-95 transition-transform shadow-lg"
          style={{ backgroundColor: tg.button, color: tg.buttonText }}
        >
          + Додати проєкт
        </button>
      )}

      <div className="flex gap-2 p-1 rounded-xl mt-1" style={{ backgroundColor: tg.secondaryBg }}>
        <button
          onClick={() => setActiveTab("projects")}
          className={`flex-1 py-2 rounded-lg font-medium transition-all ${activeTab === "projects" ? "shadow-sm" : "opacity-60"}`}
          style={{ backgroundColor: activeTab === "projects" ? tg.bgc : "transparent", color: tg.text }}
        >
          Проєкти
        </button>
        <button
          onClick={() => setActiveTab("transactions")}
          className={`flex-1 py-2 rounded-lg font-medium transition-all ${activeTab === "transactions" ? "shadow-sm" : "opacity-60"}`}
          style={{ backgroundColor: activeTab === "transactions" ? tg.bgc : "transparent", color: tg.text }}
        >
          Транзакції
        </button>
      </div>

      {activeTab === "projects" ? (
        <div className="flex flex-col gap-2 max-h-52 overflow-y-auto">
          {projects.map((proj) => (
            <div
              key={proj.id}
              onClick={() => setExpandedProjectId(expandedProjectId === proj.id ? null : proj.id)}
              className="p-4 rounded-2xl cursor-pointer transition-all"
              style={{ backgroundColor: tg.sectionBg, border: `1px solid ${tg.hint}` }}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium truncate">{proj.name}</span>
                <span className="font-semibold tabular-nums text-green-500">${proj.amount}</span>
              </div>
              {expandedProjectId === proj.id && (
                <p className="text-xs mt-3 pt-2 border-t text-left leading-relaxed animate-fade-in" style={{ color: tg.hint, borderColor: tg.secondaryBg }}>
                  {proj.description}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <TransactionList transactions={transactions} />
      )}
      
    </div>
  );
};

export default Dashboard;