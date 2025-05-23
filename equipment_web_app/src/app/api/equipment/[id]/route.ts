import { NextRequest } from 'next/server';
import { API_URL, TOKEN_URL, API_USERNAME, API_PASSWORD } from '@/lib/config';

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

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const token = await getToken();
    const response = await fetch(`${API_URL}/api/equipment/${params.id}/`, {
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Не удалось загрузить запись');
    const item = await response.json();
    return new Response(JSON.stringify(item), { headers: { 'Content-Type': 'application/json' } });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Неизвестная ошибка';
    return new Response(JSON.stringify({ error: msg }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }


  
}

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const token = await getToken();
    const body = await request.json();
    const response = await fetch(`${API_URL}/api/equipment/${params.id}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error('Не удалось обновить запись');
    const updatedItem = await response.json();
    return new Response(JSON.stringify(updatedItem), { headers: { 'Content-Type': 'application/json' } });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Неизвестная ошибка';
    return new Response(JSON.stringify({ error: msg }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const token = await getToken();
    const response = await fetch(`${API_URL}/api/equipment/${params.id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Не удалось списать оборудование');
    }
    const result = await response.json();
    return new Response(JSON.stringify(result), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Неизвестная ошибка';
    return new Response(JSON.stringify({ error: msg }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}