// Ishak: fetch /api/dashboard і POST /api/projects, заголовок Authorization з initData
import WebApp from '@twa-dev/sdk';

// 1. Дістаємо секретний рядок від Телеграму
const initData = WebApp.initData;

// 2. Вказуємо базову адресу нашого бекенду (можна буде винести в .env)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 3. Створюємо нашу власну функцію-кур'єра для запитів
export const fetchApi = async (endpoint, options = {}) => {
  
  // Збираємо запит до купи
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options, // Додаємо метод (GET, POST) і тіло запиту
    headers: {
      ...options.headers,
      // 4. Найголовніше: додаємо печатку Телеграму для бекенду
      'Authorization': `tma ${initData}`, 
      'Content-Type': 'application/json',
    },
  });
  
  // 5. Перевіряємо, чи бекенд не відправив нас куди подалі (помилка 400, 500)
  if (!response.ok) {
    // Намагаємось прочитати текст помилки від бекенду
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Помилка запиту до API');
  }
  
  // Якщо все ок, розпаковуємо JSON і віддаємо компоненту
  return response.json();
};