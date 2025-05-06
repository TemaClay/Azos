'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useSWR, { useSWRConfig } from 'swr';
import { fetcher } from '@/lib/fetcher';

interface Equipment {
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

export default function EquipmentListPage() {
  const router = useRouter();         // Хук для программной навигации


  const { data: list, error } = useSWR<Equipment[]>(
      '/api/equipment',
      fetcher,
      {
        revalidateOnFocus: false,
        dedupingInterval: 60_000,
      }
    );
    const { mutate } = useSWRConfig();
  

  // Состояние загрузки
  if (!list) return <p>Идет загрузка данных...</p>;
  
  // Обработка ошибок
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th>Артикул</th>
          <th>Инв. №</th>
          <th>Название</th>
          <th>Дата ввода</th>
          <th>Ответственный</th>
          <th>Текущая Локация</th>
          <th>Статус</th>
        </tr>
      </thead>
      <tbody>
        {list.map(item => (
          <tr
            key={item.id}
            style={{ cursor: 'pointer' }}
            onClick={() => router.push(`/equipment/${item.id}`)}
          >
            <td>{item.article}</td>
            <td>{item.inventory_number}</td>
            <td>{item.name}</td>
            <td>{item.commissioning_date}</td>
            <td>{item.equipment_manager}</td>
            <td>{item.location}</td>
            <td>{item.status.name_of_status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
