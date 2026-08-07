import { useEffect } from 'react';
import AppRouter from './router';
import { useSettingsStore } from './store';

export default function App() {
  const { theme } = useSettingsStore();

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('dark', 'light');
    root.classList.add(theme);
  }, [theme]);

  return <AppRouter />;
}
