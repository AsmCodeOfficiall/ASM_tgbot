import { useEffect, useRef } from "react";
import WebApp from "@twa-dev/sdk";

export function useMainButton({ text, enabled, onClick, visible = true }) {
  const onClickRef = useRef(onClick);
  onClickRef.current = onClick;

  useEffect(() => {
    if (!visible) return undefined;

    WebApp.MainButton.setText(text);
    WebApp.MainButton.show();

    return () => WebApp.MainButton.hide();
  }, [text, visible]);

  useEffect(() => {
    if (!visible) return;

    if (enabled) {
      WebApp.MainButton.enable();
      WebApp.MainButton.setParams({
        color: WebApp.themeParams.button_color || "#2481cc",
        text_color: WebApp.themeParams.button_text_color || "#ffffff",
      });
    } else {
      WebApp.MainButton.disable();
      WebApp.MainButton.setParams({
        color: WebApp.themeParams.secondary_bg_color || "#9ca3af",
      });
    }
  }, [enabled, visible]);

  useEffect(() => {
    if (!visible) return undefined;

    const handler = () => onClickRef.current?.();
    WebApp.onEvent("mainButtonClicked", handler);
    return () => WebApp.offEvent("mainButtonClicked", handler);
  }, [visible]);
}
