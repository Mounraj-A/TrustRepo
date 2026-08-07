import { useState } from 'react';
import { useSettingsStore } from '@/store';
import { Settings, Server, Database, Download, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

export default function SettingsPage() {
  const {
    backendUrl, timeout, maxRetries,
    setBackendUrl, setTimeout, setMaxRetries,
  } = useSettingsStore();

  const [localUrl, setLocalUrl] = useState(backendUrl);
  const [localTimeout, setLocalTimeout] = useState(timeout);
  const [localRetries, setLocalRetries] = useState(maxRetries);

  const save = () => {
    setBackendUrl(localUrl);
    setTimeout(localTimeout);
    setMaxRetries(localRetries);
    toast.success('Settings saved');
  };

  const sections = [
    {
      title: 'Backend Connection',
      icon: Server,
      content: (
        <div className="space-y-4">
          <div>
            <label className="text-xs text-muted-foreground mb-1.5 block">Backend URL</label>
            <input
              value={localUrl}
              onChange={e => setLocalUrl(e.target.value)}
              className="w-full max-w-md px-3 py-2 text-sm rounded-lg border border-border bg-background focus:ring-1 focus:ring-primary focus:outline-none font-mono"
              placeholder="http://127.0.0.1:8000"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1.5 block">Request Timeout (ms)</label>
            <input
              type="number"
              value={localTimeout}
              onChange={e => setLocalTimeout(Number(e.target.value))}
              className="w-32 px-3 py-2 text-sm rounded-lg border border-border bg-background focus:ring-1 focus:ring-primary focus:outline-none"
            />
          </div>
          <div>
            <label className="text-xs text-muted-foreground mb-1.5 block">Max Retries</label>
            <input
              type="number"
              min={0} max={10}
              value={localRetries}
              onChange={e => setLocalRetries(Number(e.target.value))}
              className="w-24 px-3 py-2 text-sm rounded-lg border border-border bg-background focus:ring-1 focus:ring-primary focus:outline-none"
            />
          </div>
        </div>
      ),
    },
    {
      title: 'About',
      icon: Database,
      content: (
        <div className="space-y-2 text-sm text-muted-foreground">
          <p>TrustRepo Enterprise Intelligence Platform</p>
          <p>Version: <span className="font-mono text-foreground">3.0.0</span></p>
          <p>Backend: <span className="font-mono text-primary">{backendUrl}</span></p>
          <p className="text-xs mt-3 flex items-start gap-1.5">
            <AlertTriangle size={12} className="text-amber-400 mt-0.5 shrink-0" />
            Restart the Vite dev server after changing the backend URL to update the proxy configuration.
          </p>
        </div>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6 animate-in">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Settings size={20} className="text-primary" />
        Settings
      </h1>

      {sections.map(({ title, icon: Icon, content }) => (
        <div key={title} className="glass rounded-2xl p-6">
          <h2 className="text-sm font-semibold flex items-center gap-2 mb-5">
            <Icon size={14} className="text-primary" />
            {title}
          </h2>
          {content}
        </div>
      ))}

      <div className="flex justify-end">
        <button
          onClick={save}
          className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-lg gradient-trust text-white
                     hover:opacity-90 transition-opacity active:scale-95"
        >
          <Download size={14} />
          Save Settings
        </button>
      </div>
    </div>
  );
}
