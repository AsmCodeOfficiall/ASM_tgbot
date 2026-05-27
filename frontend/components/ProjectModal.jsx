import { useState } from "react";
import WebApp from "@twa-dev/sdk";
import { fetchApi } from "../api";
import { useMainButton } from "../hooks/useMainButton";
import { useTelegramBackButton } from "../hooks/useTelegramBackButton";
import { tg } from "../utils/theme";

const ProjectModal = ({ onClose, onSuccess }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isValid =
    name.trim() !== "" && amount !== "" && parseFloat(amount) > 0;

  useTelegramBackButton(onClose, true);

  useMainButton({
    text: "Додати проєкт",
    enabled: isValid && !isSubmitting,
    visible: true,
    onClick: async () => {
      if (!isValid || isSubmitting) return;

      setIsSubmitting(true);
      WebApp.MainButton.showProgress();

      try {
        await fetchApi("/api/projects", {
          method: "POST",
          body: JSON.stringify({
            name: name.trim(),
            description: description.trim(),
            amount: parseFloat(amount),
          }),
        });

        WebApp.HapticFeedback.notificationOccurred("success");
        await onSuccess();
        onClose();
      } catch (error) {
        console.error("Помилка:", error);
        WebApp.HapticFeedback.notificationOccurred("error");
        WebApp.showAlert(
          error.message || "Не вдалося створити проєкт. Спробуйте ще раз."
        );
      } finally {
        WebApp.MainButton.hideProgress();
        setIsSubmitting(false);
      }
    },
  });

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col justify-end"
      style={{ backgroundColor: "rgba(0,0,0,0.45)" }}
      onClick={onClose}
    >
      <div
        className="w-full rounded-t-3xl p-6 pb-8 max-h-[85vh] overflow-y-auto"
        style={{
          backgroundColor: tg.bg,
          color: tg.text,
          paddingBottom: "calc(2rem + env(safe-area-inset-bottom, 0px))",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Новий проєкт</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl leading-none p-1"
            style={{ color: tg.hint }}
            aria-label="Закрити"
          >
            ✕
          </button>
        </div>

        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => e.preventDefault()}
        >
          <div>
            <label className="block text-sm mb-1.5" style={{ color: tg.hint }}>
              Назва проєкту
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Наприклад: Бот для клієнта"
              autoComplete="off"
              className="w-full rounded-xl px-4 py-3 outline-none"
              style={{
                backgroundColor: tg.secondaryBg,
                color: tg.text,
                border: `1px solid ${tg.hint}`,
              }}
            />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: tg.hint }}>
              Опис проєкту
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Короткий опис, деталі або посилання на ТЗ..."
              rows="3"
              className="w-full rounded-xl px-4 py-3 outline-none resize-none"
              style={{
                backgroundColor: tg.secondaryBg,
                color: tg.text,
                border: `1px solid ${tg.hint}`,
              }}
            />
          </div>
            
          <div>
            <label className="block text-sm mb-1.5" style={{ color: tg.hint }}>
              Сума (USD)
            </label>
            <input
              type="number"
              inputMode="decimal"
              min="0"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              className="w-full rounded-xl px-4 py-3 outline-none tabular-nums"
              style={{
                backgroundColor: tg.secondaryBg,
                color: tg.text,
                border: `1px solid ${tg.hint}`,
              }}
            />
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProjectModal;
