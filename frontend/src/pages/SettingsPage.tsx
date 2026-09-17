import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Globe, Database, LogOut, Save } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';

export function SettingsPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const [notifications, setNotifications] = useState({
    analysisComplete: true,
    newRecommendations: true,
    evidenceUpdates: false,
    weeklyDigest: true,
  });

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => setSaving(false), 800);
  };

  return (
    <div className="space-y-6 animate-in">
      <PageHeader title="Settings" description="Manage your account preferences and configuration." />

      {/* Account */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Account</CardTitle>
          <CardDescription>Update your personal information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="fullName">Full name</Label>
              <Input id="fullName" defaultValue={user?.fullName || ''} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" defaultValue={user?.email || ''} disabled />
            </div>
            <div className="space-y-2">
              <Label htmlFor="org">Organization</Label>
              <Input id="org" defaultValue={user?.organization || ''} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Input id="role" defaultValue={user?.role || ''} disabled />
            </div>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="mr-2 h-4 w-4" />
            {saving ? 'Saving...' : 'Save changes'}
          </Button>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-primary" />
            <div>
              <CardTitle className="text-base">Notifications</CardTitle>
              <CardDescription>Choose what you want to be notified about</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-1">
          <ToggleRow
            label="Analysis complete"
            description="Get notified when an analysis finishes running"
            checked={notifications.analysisComplete}
            onChange={(v) => setNotifications({ ...notifications, analysisComplete: v })}
          />
          <Separator />
          <ToggleRow
            label="New recommendations"
            description="Get notified when new recommendations are generated"
            checked={notifications.newRecommendations}
            onChange={(v) => setNotifications({ ...notifications, newRecommendations: v })}
          />
          <Separator />
          <ToggleRow
            label="Evidence updates"
            description="Get notified when new evidence is added to the library"
            checked={notifications.evidenceUpdates}
            onChange={(v) => setNotifications({ ...notifications, evidenceUpdates: v })}
          />
          <Separator />
          <ToggleRow
            label="Weekly digest"
            description="Receive a weekly summary of your environmental data"
            checked={notifications.weeklyDigest}
            onChange={(v) => setNotifications({ ...notifications, weeklyDigest: v })}
          />
        </CardContent>
      </Card>

      {/* API Configuration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-primary" />
            <div>
              <CardTitle className="text-base">API Configuration</CardTitle>
              <CardDescription>Backend connection settings</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="apiUrl">API Base URL (VITE_API_BASE_URL)</Label>
            <Input
              id="apiUrl"
              value={import.meta.env.VITE_API_BASE_URL || 'Not configured — running in mock mode'}
              disabled
            />
            <p className="text-xs text-muted-foreground">
              When configured, all services will fetch data from this API endpoint.
              Without it, TerraSage uses built-in mock data for demonstration.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Card className="border-destructive/20">
        <CardHeader>
          <div className="flex items-center gap-2">
            <LogOut className="h-4 w-4 text-destructive" />
            <CardTitle className="text-base text-destructive">Session</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={handleLogout} className="text-destructive hover:text-destructive">
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-foreground">{label}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <Switch checked={checked} onCheckedChange={onChange} />
    </div>
  );
}
