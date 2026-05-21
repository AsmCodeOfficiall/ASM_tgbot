import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";

const THEME_KEYS = [
  "bg_color",
  "text_color",
  "hint_color",
  "link_color",
  "button_color",
  "button_text_color",
  "secondary_bg_color",
  "header_bg_color",
  "accent_text_color",
  "section_bg_color",
  "section_header_text_color",
  "subtitle_text_color",
  "destructive_text_color",
];

function applyThemeParams(params) {
  const root = document.documentElement;
  THEME_KEYS.forEach((key) => {
    const value = params[key];
    if (value) {
      root.style.setProperty(`--tg-theme-${key.replace(/_/g, "-")}`, value);
    }
  });
}

export function useTelegramTheme() {
  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
    applyThemeParams(WebApp.themeParams);

    const onThemeChanged = () => applyThemeParams(WebApp.themeParams);
    WebApp.onEvent("themeChanged", onThemeChanged);

    return () => WebApp.offEvent("themeChanged", onThemeChanged);
  }, []);
}
