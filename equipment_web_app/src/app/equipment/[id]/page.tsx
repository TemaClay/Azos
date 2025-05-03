'use client';

import React from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { usePathname } from 'next/navigation';
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

/**
 * Компонент страницы детализации оборудования с продвинутой стратегией кэширования
 * 
 * - При монтировании компонента проверяется наличие данных в SWR-кэше
 * - Если данные в кэше присутствуют:
 *   - Мгновенно отображаются (через fallbackData)
 *   - Запрос к API не выполняется (revalidateOnMount: false)
 * - Если данных в кэше нет:
 *   - Выполняется запрос к API
 *   - Результат автоматически сохраняется в кэш
 */
export default function EquipmentDetailPage() {
    // Хуки для работы с маршрутизацией и кэшем
    const pathname = usePathname(); // Получение текущего URL
    const id = pathname.split('/').pop() as string; // Извлечение ID оборудования
    const { cache } = useSWRConfig(); // Доступ к глобальному кэшу SWR
    const swrKey = `/api/equipment/${id}`; // Ключ для кэширования
  
    // Проверка существования кэшированных данных
    const cachedData = cache.get(swrKey)?.data as EquipmentDetail | undefined;
  
    // Конфигурация SWR с учетом состояния кэша
    const { data: item, error } = useSWR<EquipmentDetail>(
      swrKey,
      fetcher,
      {
        revalidateOnMount: !cachedData, // Запрос ТОЛЬКО при отсутствии данных
        revalidateIfStale: false, // Не обновлять устаревшие данные
        revalidateOnFocus: false, // Игнорировать фокус окна
        dedupingInterval: 3_600_000, // 1 час защиты от дублирования
        fallbackData: cachedData, // Использование кэша как начальных данных
      }
    );
  
    // Обработка состояния ошибки
    if (error) return <p style={{ color: 'red' }}>Ошибка: {error.message}</p>;
    
    // Состояние загрузки (срабатывает только при отсутствии кэша)
    if (!item) return <p>Загрузка…</p>;

  return (
    <div style={{ padding: 20 }}>
      <h1>Детали оборудования #{item.id}</h1>
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
    </div>
  );
}