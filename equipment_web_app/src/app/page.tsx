import { EquipmentFetcher } from '@/components/EquipmentFetcher';

export default function Home() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>Оборудование</h1>
      <EquipmentFetcher />
    </main>
  );
}
