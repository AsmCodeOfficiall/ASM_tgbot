import { tg } from "../utils/theme";
import { useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "../api";
import gearIcon from "../assets/gear.png";
import checkStatic from "../assets/success.png";

export default function OnboardingScreen({ onFinish }) {
    const [teamName, setTeamName] = useState("");
    const [tax, settax] = useState(10);
    const [isSpinning, setIsSpinning] = useState(false);
    const [step, setStep] = useState("welcome");
    const [copied, setCopied] = useState(false);
    
    const [inviteCode, setInviteCode] = useState("");
    const botUsername = "AsmCode";
    const realInviteLink = `https://t.me/${botUsername}?startapp=${inviteCode}`;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSpinning(true);

        try {
            const response = await fetchApi("/api/teams", {
                method: "POST",
                body: JSON.stringify({ 
                    name: teamName, 
                    tax: Number(tax)
                })
            });
            setInviteCode(response.team.invite_code);
            
            WebApp.HapticFeedback.notificationOccurred("success");
            setStep("success");
        } catch (error) {
            console.error("Ошибка:", error);
            WebApp.HapticFeedback.notificationOccurred("error");
            WebApp.showAlert(error.message || "Не вдалося створити команду");
        } finally {
            setIsSpinning(false);
        }
    };

    const handleCopyLink = () => {
        navigator.clipboard.writeText(realInviteLink);
        setCopied(true);
        WebApp.HapticFeedback.impactOccurred("light");
        setTimeout(() => setCopied(false), 2000);
    };

    if (step === "welcome") {
        return (
            <div className="flex flex-1 flex-col justify-center items-center gap-4 min-h-[50vh] text-center p-4 animate-fade-in">
                <div className="text-7xl mb-2">🚀</div>
                <h2 className="text-2xl font-bold" style={{ color: tg.text }}>
                    Вітаємо в системі!
                </h2>
                <p className="text-base leading-relaxed" style={{ color: tg.hint }}>
                    Ви ще не перебуваєте в жодній команді. Створіть свою першу команду, щоб почати працювати з бюджетом та залучати розробників.
                </p>
                <button
                    type="button"
                    onClick={() => setStep("form")}
                    className="w-full font-semibold py-3 px-4 mt-4 rounded-xl shadow-lg active:scale-95 transition-transform"
                    style={{ backgroundColor: tg.button, color: tg.buttonText }}
                >
                    Створити команду
                </button>
            </div>
        )
    }

    if (step === "success") {
        return (
            <div className="flex flex-1 flex-col justify-center items-center gap-4 min-h-[50vh] text-center p-4 animate-fade-in">
                <img 
                    src={checkStatic} 
                    alt="Успіх" 
                    className="w-32 h-32 mb-2 object-contain" 
                />
                <h2 className="text-2xl font-bold" style={{ color: tg.text }}>
                    Вітаю!
                </h2>
                <p className="text-lg" style={{ color: tg.text }}>
                    Команда <span className="font-bold text-xl" style={{ color: tg.text }}>«{teamName}»</span> успішно створена!
                </p>

                <div className="w-full mt-6 flex flex-col gap-2 text-left">
                    <p className="text-sm font-medium ml-1" style={{ color: tg.hint }}>
                        Запросіть учасників за цим посиланням:
                    </p>
                    <div 
                        onClick={handleCopyLink}
                        className="flex items-center justify-between p-4 rounded-xl cursor-pointer active:scale-95 transition-all shadow-md"
                        style={{
                            backgroundColor: tg.secondaryBg,
                            border: `1px solid ${copied ? '#10B981' : tg.button}`
                        }}
                    >
                        <span className="truncate mr-4 text-sm font-medium" style={{ color: tg.text }}>
                            {realInviteLink}
                        </span>
                        <span className="text-2xl min-w-[30px] text-center">
                            {copied ? "✅" : "📋"}
                        </span>
                    </div>
                    
                    <button
                        type="button"
                        onClick={onFinish}
                        className="w-full font-semibold py-3 px-4 mt-4 rounded-xl shadow-lg active:scale-95 transition-transform"
                        style={{ backgroundColor: tg.button, color: tg.buttonText }}
                    >
                        Далі
                    </button>
                </div>
            </div>    
        );
    }

    return (
        <div className="flex flex-1 flex-col justify-center p-4 animate-fade-in">
            <img 
                src={gearIcon} 
                alt="Налаштування" 
                className={`w-36 h-36 mx-auto relative -top-12 mb-4 object-contain transition-transform
                    duration-700 ease-in-out ${isSpinning ? "rotate-[360deg]" : "rotate-0"}`}
            />
            <h2 className="text-2xl font-bold mb-6 text-center" style={{ color: tg.text }}>
                Налаштування команди
            </h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                    <label className="font-medium" style={{ color: tg.hint }}>
                        Назва команди
                    </label>
                    <input
                        type="text"
                        value={teamName}
                        onChange={(e) => setTeamName(e.target.value)}
                        placeholder="Наприклад: ВЕБ-Відділ"
                        required
                        className="p-3 rounded-xl border-none outline-none focus:ring-2"
                        style={{ backgroundColor: tg.secondaryBg, color: tg.text, ringColor: tg.button }}
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label className="font-medium" style={{ color: tg.hint }}>
                        Відсоток у спільний фонд (%)
                    </label>
                    <input
                        type="number"
                        min="0"
                        max="100"
                        value={tax}
                        onChange={(e) => {
                            let val = e.target.value;
                            if (val === "") { settax(""); return; }
                            if (val.length > 1 && val.startsWith("0")) {
                              val = parseInt(val, 10).toString(); 
                            }
                            const num = Number(val);
                            if (!isNaN(num) && num >= 0 && num <= 100) { settax(val); }
                          }}
                        required
                        className="p-3 rounded-xl border-none outline-none focus:ring-2"
                        style={{ backgroundColor: tg.secondaryBg, color: tg.text, ringColor: tg.button }}
                    />
                </div>
                <div className="flex gap-2 mt-4">
                    <button
                        type="button"
                        onClick={() => setStep("welcome")}
                        className="flex-1 font-semibold py-3 px-4 rounded-xl active:scale-95 transition-transform"
                        style={{ backgroundColor: tg.secondaryBg, color: tg.text }}
                    >
                        Назад
                    </button>
                    <button
                        type="submit"
                        disabled={isSpinning}
                        className="flex-1 font-semibold py-3 px-4 rounded-xl shadow-lg active:scale-95 transition-transform disabled:opacity-50"
                        style={{ backgroundColor: tg.button, color: tg.buttonText }}
                    >
                        {isSpinning ? "Збереження..." : "Зберегти"}
                    </button>
                </div>
            </form>
        </div>
    );
}