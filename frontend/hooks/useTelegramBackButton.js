import { useEffect } from "react";
import WebApp from "@twa-dev/sdk";

export function useTelegramBackButton(onBack, visible = true) {
  useEffect(() => {
    if (!visible) return undefined;

    WebApp.BackButton.show();
    WebApp.onEvent("backButtonClicked", onBack);

    return () => {
      WebApp.BackButton.hide();
      WebApp.offEvent("backButtonClicked", onBack);
    };
  }, [onBack, visible]);
}
