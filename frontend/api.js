import WebApp from "@twa-dev/sdk";

const initData = WebApp.initData;

// Hugging Face Space: API and Mini App on the same domain (:7860), BASE_URL is empty.
// Locally Vite proxy redirects /api → localhost:7860
const BASE_URL = import.meta.env.VITE_API_URL ?? "";

function parseErrorDetail(detail) {
  if (!detail) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || d.message || String(d)).join(", ");
  }
  return String(detail);
}

export const fetchApi = async (endpoint, options = {}) => {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `tma ${initData}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      parseErrorDetail(errorData.detail) || "Помилка запиту до API"
    );
  }

  if (response.status === 204) return null;
  return response.json();
};
