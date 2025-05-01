'use client'
import React, { useState } from 'react';

interface Equipment {
  id: number;
  article: string;
  inventory_number: string;
  name: string;
  commissioning_date: string;
  equipment_manager: string;
  location: string;
  default_location: number;
  status: number;
}

export const EquipmentFetcher: React.FC = () => {
  const [data, setData] = useState<Equipment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEquipment = async () => {
    setLoading(true);
    setError(null);

    try {
      const tokenRes = await fetch('http://localhost:8000/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'admin' }),
      });
      if (!tokenRes.ok) throw new Error('Ошибка получения токена');

      const { access: token } = await tokenRes.json();

      const eqRes = await fetch('http://localhost:8000/api/equipment/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!eqRes.ok) throw new Error('Ошибка получения оборудования');

      const equipmentList: Equipment[] = await eqRes.json();
      setData(equipmentList);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={fetchEquipment} disabled={loading}>
        {loading ? 'Загрузка…' : 'Загрузить оборудование'}
      </button>

      {error && <p style={{ color: 'red' }}>Ошибка: {error}</p>}

      {data.length > 0 && (
        <table style={{ marginTop: 20, borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Артикул</th>
              <th>Инвентарный №</th>
              <th>Название</th>
              <th>Дата ввода</th>
              <th>Ответственный</th>
              <th>Текущее место</th>
              <th>Локация по умолчанию</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {data.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.article}</td>
                <td>{item.inventory_number}</td>
                <td>{item.name}</td>
                <td>{item.commissioning_date}</td>
                <td>{item.equipment_manager}</td>
                <td>{item.location}</td>
                <td>{item.default_location}</td>
                <td>{item.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
