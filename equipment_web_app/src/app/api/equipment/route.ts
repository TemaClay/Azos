// app/api/equipment/route.ts
import { NextRequest } from 'next/server';
import { API_URL, TOKEN_URL, API_USERNAME, API_PASSWORD } from '@/lib/config'; // Импортируем переменные из config

// Получение токена для доступа
async function getToken() {
  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: API_USERNAME, password: API_PASSWORD }),
  });

  if (!res.ok) throw new Error('Ошибка при получении токена');

  const { access: token } = await res.json();
  return token;
}

// Обработчик запроса к DRF для получения оборудования
export async function GET(request: NextRequest) {
  try {
    // Получаем токен для аутентификации
    const token = await getToken();

    // Делаем запрос к внешнему API (DRF) для получения списка оборудования
    const response = await fetch(`${API_URL}/api/equipment/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Ошибка при загрузке данных оборудования');
    }

    // Получаем данные оборудования из ответа
    const equipment = await response.json();

    // Возвращаем данные клиенту
    return new Response(JSON.stringify(equipment), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: unknown) {
    // Обрабатываем ошибку, если она возникла
    if (error instanceof Error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Если ошибка не является экземпляром Error, возвращаем общую ошибку
    return new Response(JSON.stringify({ error: 'Неизвестная ошибка' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
