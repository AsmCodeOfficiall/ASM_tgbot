import { useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "../api";
import { tg } from "../utils/theme";

const Settingsboard = ({ role, onBack, teamName, tax, members = [], inviteCode, onRefresh }) => {
  const [copied, setCopied] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const botUsername = "AsmCode_bot"; 
  const realInviteLink = `https://t.me/${botUsername}?start=invite_${inviteCode}`;
  const isLead = role === "leader";
  const [localTax, setLocalTax] = useState(tax ?? 10);
  const [localTaxes, setLocalTaxes] = useState(() => {
    const initialTaxes = {};
    members.forEach((m) => {
      initialTaxes[m.id] = m.payout_percent ?? 0;
    });
    return initialTaxes;
  });

  const handleCopyLink = () => {
    navigator.clipboard.writeText(realInviteLink);
    setCopied(true);
    WebApp.HapticFeedback.impactOccurred("light");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTaxChange = (memberId, value) => {
    if (!isLead) return;

    if (value === "") {
      setLocalTaxes((prev) => ({ ...prev, [memberId]: "" }));
      return;
    }
    let parsed = parseInt(value, 10);
    if (isNaN(parsed) || parsed < 0) parsed = 0;
    if (parsed > 100) parsed = 100;
    setLocalTaxes((prev) => ({ ...prev, [memberId]: parsed }));
  };

  const handleSave = async () => {
    if (!isLead) return;

    setIsSaving(true);
    WebApp.MainButton.showProgress();

    try {
      const updatedMembers = members.map((m) => ({
        id: m.id,
        personal_tax: Number(localTaxes[m.id] || 0),
      }));

      await fetchApi("/api/teams/members", {
        method: "PUT",
        body: JSON.stringify({
          tax: Number(localTax || 0),
          members: updatedMembers,
        }),
      });

      WebApp.HapticFeedback.notificationOccurred("success");
      if (onRefresh) await onRefresh();
      onBack();
    } catch (error) {
      console.error("Помилка збереження налаштувань:", error);
      WebApp.HapticFeedback.notificationOccurred("error");
      WebApp.showAlert(error.message || "Не вдалося зберегти налаштування.");
    } finally {
      WebApp.MainButton.hideProgress();
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 animate-fade-in">
      
      <div className="flex items-center gap-3 mb-2">
      <button
          type="button"
          onClick={onBack}
          className="p-2.5 rounded-xl active:scale-95 transition-transform flex items-center justify-center"
          style={{ backgroundColor: tg.secondaryBg, color: tg.text }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <div>
          <h1 className="text-xl font-bold" style={{ color: tg.text }}>
            Налаштування команди
          </h1>
        </div>
      </div>

      <div className="flex flex-col gap-1.5 text-left">
        <label className="text-xs font-medium ml-1" style={{ color: tg.hint }}>
          Посилання для запрошення розробників:
        </label>
        <div 
          onClick={handleCopyLink}
          className="flex items-center justify-between p-4 rounded-2xl cursor-pointer active:scale-95 transition-all shadow-sm"
          style={{
            backgroundColor: tg.secondaryBg,
            border: `1px solid ${copied ? '#10B981' : 'transparent'}`,
          }}
        >
          <span className="truncate mr-4 text-sm font-medium" style={{ color: tg.text }}>
            {realInviteLink}
          </span>
          <span className="text-xl min-w-[30px] text-center shrink-0">
            {copied ? "✅" : "📋"}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-1.5 text-left">
        <label className="text-xs font-medium ml-1" style={{ color: tg.hint }}>
          Відсоток у спільний фонд команди (%):
        </label>
        <div 
          className="flex items-center justify-between px-4 py-2.5 rounded-2xl"
          style={{ backgroundColor: tg.secondaryBg }}
        >
          <input
            type="number"
            inputMode="numeric"
            min="0"
            max="100"
            value={localTax}
            onChange={(e) => {
              if (!isLead) return;
              let val = e.target.value;
              if (val === "") { setLocalTax(""); return; }
              let parsed = parseInt(val, 10);
              if (isNaN(parsed) || parsed < 0) parsed = 0;
              if (parsed > 100) parsed = 100;
              setLocalTax(parsed);
            }}
            readOnly={!isLead}
            className="w-full bg-transparent border-none outline-none font-semibold text-sm"
            style={{ color: tg.text, opacity: isLead ? 1 : 0.7 }}
            placeholder="10"
          />
          <span className="text-sm font-bold opacity-50 ml-2" style={{ color: tg.text }}>%</span>
        </div>
      </div>    

      <div className="flex flex-col gap-2 mt-1">
        <label className="text-xs font-medium ml-1 text-left" style={{ color: tg.hint }}>
          Розподіл часток учасників (%):
        </label>

        {!members.length ? (
          <p className="text-sm text-center p-4" style={{ color: tg.hint }}>
            У команді ще немає учасників
          </p>
        ) : (
          <div className="flex flex-col gap-3 max-h-56 overflow-y-auto pr-1">
            {members.map((member) => {
              const currentTax = localTaxes[member.id] !== "" ? Number(localTaxes[member.id]) : 0;

              return (
                <div 
                  key={member.id}
                  className="flex flex-col p-3 rounded-2xl"
                  style={{ backgroundColor: tg.sectionBg }}
                >
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex items-center gap-3 min-w-0">
                      <div 
                        className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold shrink-0"
                        style={{ backgroundColor: tg.button, color: tg.buttonText }}
                      >
                        {member.name ? member.name.charAt(0).toUpperCase() : "U"}
                      </div>
                      
                      <div className="flex flex-col min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold truncate" style={{ color: tg.text }}>
                            {member.name || "Розробник"}
                          </span>
                          <span 
                            className="text-[9px] px-1.5 py-0.5 rounded uppercase font-bold"
                            style={{ 
                              backgroundColor: member.role === "leader" ? "rgba(245, 158, 11, 0.15)" : tg.secondaryBg,
                              color: member.role === "leader" ? "#f59e0b" : tg.link
                            }}
                          >
                            {member.role === "leader" ? "Тімлід" : "Розробник"}
                          </span>
                        </div>
                        <span className="text-xs mt-0.5" style={{ color: tg.hint }}>
                          Баланс: ${member.balance?.toFixed(2) || "0.00"}
                        </span>
                      </div>
                    </div>

                    <div 
                      className="flex items-center justify-center rounded-xl px-2 py-1.5 shrink-0"
                      style={{ backgroundColor: tg.secondaryBg, minWidth: '60px' }}
                    >
                      <input
                        type="number"
                        inputMode="numeric"
                        min="0"
                        max="100"
                        value={localTaxes[member.id] ?? ""}
                        onChange={(e) => handleTaxChange(member.id, e.target.value)}
                        readOnly={!isLead}
                        className="bg-transparent border-none outline-none text-center font-bold tabular-nums text-sm p-0 m-0 focus:ring-0"
                        style={{ color: tg.text, width: '3ch', opacity: isLead ? 1 : 0.7 }}
                      />
                      <span className="text-sm font-bold" style={{ color: tg.text }}>%</span>
                    </div>
                  </div>

                  <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: tg.secondaryBg }}>
                    <div 
                      className="h-full transition-all duration-500 ease-out rounded-full"
                      style={{ 
                        width: `${currentTax}%`, 
                        backgroundColor: tg.button,
                        opacity: currentTax === 0 ? 0 : 1 
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {isLead && (
        <button
          type="button"
          disabled={isSaving}
          onClick={handleSave}
          className="w-full font-semibold py-3 px-4 mt-2 rounded-xl shadow-lg active:scale-95 transition-transform disabled:opacity-50"
          style={{ backgroundColor: tg.button, color: tg.buttonText }}
        >
          {isSaving ? "Збереження..." : "Зберегти зміни"}
        </button>
      )}

    </div>
  );
};

export default Settingsboard;