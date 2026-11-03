import { useEffect, useState, type ReactNode } from 'react';
import { Menu } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { Button } from '@/components/ui/button';
import { request } from '@/services/http';

interface AppShellProps {
  children: ReactNode;
}

type BackendStatus = 'checking' | 'connected' | 'database-unavailable' | 'unavailable';

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');

  useEffect(() => {
    let active = true;
    const checkBackend = () => {
      request<{ status: string; database: string }>('/api/health')
        .then((health) => {
          if (active) {
            setBackendStatus(
              health.status === 'ok' && health.database === 'connected'
                ? 'connected'
                : 'database-unavailable',
            );
          }
        })
        .catch(() => {
          if (active) setBackendStatus('unavailable');
        });
    };

    checkBackend();
    const intervalId = window.setInterval(checkBackend, 30_000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const statusLabel: Record<BackendStatus, string> = {
    checking: 'Checking Backend',
    connected: 'Live Backend Connected',
    'database-unavailable': 'Backend Database Unavailable',
    unavailable: 'Backend Unavailable',
  };
  const statusStyle: Record<BackendStatus, string> = {
    checking: 'border-border bg-muted text-muted-foreground',
    connected: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
    'database-unavailable': 'border-amber-500/20 bg-amber-500/10 text-amber-700 dark:text-amber-400',
    unavailable: 'border-destructive/20 bg-destructive/10 text-destructive',
  };

  return (
    <div className="min-h-screen bg-background">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/80 px-4 backdrop-blur-md lg:px-8">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex-1" />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${statusStyle[backendStatus]}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${backendStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-current'}`} />
              {statusLabel[backendStatus]}
            </span>
          </div>
        </header>
        <main className="px-4 py-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
