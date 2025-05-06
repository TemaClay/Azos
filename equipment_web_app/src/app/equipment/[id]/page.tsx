'use client';

import React, { useState } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { usePathname, useRouter } from 'next/navigation';
import { fetcher } from '@/lib/fetcher';


interface EquipmentDetail {
  id: number;
  article: string;
  inventory_number: string;
  name: string;
  commissioning_date: string;
  equipment_manager: string;
  location: string;
  default_location: Place;
  status: Status;
}

interface Place {
  id: number;
  name: string;
}

interface Status {
  id: number;
  name_of_status: string;
}

export default function EquipmentDetailPage() {
  const pathname = usePathname();
  const router = useRouter();      
  const id = pathname.split('/').pop() as string;
  const { cache, mutate } = useSWRConfig();
  const swrKey = `/api/equipment/${id}`;
  const cachedData = cache.get(swrKey)?.data as EquipmentDetail | undefined;

  const { data: item, error } = useSWR<EquipmentDetail>(swrKey, fetcher, {
    revalidateOnMount: !cachedData,
    revalidateIfStale: false,
    revalidateOnFocus: false,
    dedupingInterval: 3_600_000,
    fallbackData: cachedData,
  });

  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<EquipmentDetail>>({});

  if (error) return <p style={{ color: 'red' }}>Ошибка: {error.message}</p>;
  if (!item) return <p>Загрузка…</p>;

  const handleEditClick = () => {
    setIsEditing(true);
    setFormData({
      article: item.article,
      inventory_number: item.inventory_number,
      name: item.name,
      commissioning_date: item.commissioning_date,
      equipment_manager: item.equipment_manager,
      location: item.location,
      status: item.status,
    });
  };
  /*Функция, добавляющая для аппарата статус "Списано". Отправляет запрос через API на Django с методом
  DELETE, возвращает пользователя обратно на страницу Equipment. */ 
  const handleDiscardClick = async () => {
    if (!confirm('Вы уверены, что хотите списать это оборудование?')) return;

    try {
      const res = await fetch(`/api/equipment/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Не удалось списать оборудование');
      }

      // Обновляем локальный кэш списка, теперь без этого оборудования
      mutate<EquipmentDetail[]>(
        '/api/equipment',
        (current = []) => current.filter(e => e.id !== Number(id)),
        { revalidate: false }
      );

      router.push('/equipment'); // переходим на список
    } catch (e) {
      console.error(e);
      alert((e as Error).message);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/equipment/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Ошибка при сохранении изменений');

      const updatedItem = await response.json();
      mutate(swrKey, updatedItem, false);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Детали оборудования #{item.id}</h1>
      <button onClick={handleEditClick} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
        ✏️
      </button>
      <button onClick={handleDiscardClick} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
      ⛔️
      </button>
      {isEditing ? (
        <div>
          <label>
            Название:
            <input name="name" value={formData.name || ''} onChange={handleChange} />
          </label>
          <label>
            Артикул:
            <input name="article" value={formData.article || ''} onChange={handleChange} />
          </label>
          <label>
            Инв. №:
            <input name="inventory_number" value={formData.inventory_number || ''} onChange={handleChange} />
          </label>
          <label>
            Ответственный:
            <input name="equipment_manager" value={formData.equipment_manager || ''} onChange={handleChange} />
          </label>
          <label>
            Дата ввода:
            <input name="commissioning_date" value={formData.commissioning_date || ''} onChange={handleChange} />
          </label>
          <label>
            Местоположение:
            <input name="location" value={formData.location || ''} onChange={handleChange} />
          </label>
          <label>
            Статус:
            <input name="status" value={formData.status?.name_of_status || ''} onChange={handleChange} />
          </label>
          <button onClick={handleSave}>Сохранить</button>
        </div>
      ) : (
        <p>
          Название: {item.name} &nbsp;&nbsp;
          Артикул: {item.article} &nbsp;&nbsp;
          Инв. №: {item.inventory_number} &nbsp;&nbsp;
          Ответственный: {item.equipment_manager} &nbsp;&nbsp;
          Дата ввода: {item.commissioning_date} &nbsp;&nbsp;
          Местоположение: {item.location} &nbsp;&nbsp;
          Локация по умолчанию: {item.default_location.name} &nbsp;&nbsp;
          Статус: {item.status.name_of_status}
        </p>
      )}
    </div>
  );
}
