'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSWRConfig } from 'swr';

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
  const { cache, mutate } = useSWRConfig(); // Инструменты управления SWR-кэшем
  const [list, setList] = useState<Equipment[] | null>(null); // Локальное состояние списка
  const [error, setError] = useState<string | null>(null);    // Состояние ошибки

  useEffect(() => {
    const loadData = async () => {
      try {
        // Основной запрос на получение полного списка оборудования
        const res = await fetch('/api/equipment', {
          cache: 'no-cache',    // Использовать кэш браузера
          next: { revalidate: 100 } // Фоновая ревалидация через 100 сек
        });

        const data: Equipment[] = await res.json();
        setList(data); // Обновление локального состояния для рендеринга
        
        console.log('equipment list', data);
        /**
         * Кэшируем полный список оборудования.
         * mutate с флагом false - обновление кэша без повторной валидации.
         * Это позволяет последующим запросам к /api/equipment использовать кэшированные данные.
         */
        mutate('/api/equipment', data, false);

        /**
         * Инкрементальное кэширование элементов:
         * - Итерируем по полученному списку
         * - Для каждого элемента создаем ключ вида /api/equipment/[id]
         * - Сохраняем в кэш ТОЛЬКО если элемент отсутствует
         * 
         * Эффект для подстраниц:
         * При переходе на /equipment/[id] SWR автоматически проверит кэш:
         * 1. Если данные есть - мгновенно отобразит их
         * 2. Если нет - выполнит запрос к /api/equipment/[id]
         * 
         * Таким образом, первый запрос к списку предзагружает данные
         * для ВСЕХ возможных подстраниц, уменьшая нагрузку на бэкенд.
         */
        data.forEach((item) => {
          const key = `/api/equipment/${item.id}`;
          if (!cache.get(key)) {
            mutate(key, item, false);
          }
        });

      } catch (err: any) {
        setError(err.message || 'Ошибка загрузки данных');
      }
    };

    loadData();
  }, [mutate, cache]); // Зависимости гарантируют актуальность кэша

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
