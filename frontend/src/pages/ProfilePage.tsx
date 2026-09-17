import { Link } from 'react-router-dom';
import { Mail, Building2, Calendar, Microscope, BookOpen, MessageSquare, Lightbulb, Settings } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { PageHeader } from '@/components/shared/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  const initials = user.fullName
    ?.split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('') || 'TS';

  const stats = [
    { icon: Microscope, label: 'Analyses run', value: '5', color: 'text-primary bg-primary/10' },
    { icon: MessageSquare, label: 'Conversations', value: '3', color: 'text-chart-3 bg-chart-3/10' },
    { icon: Lightbulb, label: 'Recommendations', value: '8', color: 'text-warning bg-warning/10' },
    { icon: BookOpen, label: 'Evidence sources', value: '12', color: 'text-success bg-success/10' },
  ];

  return (
    <div className="space-y-6 animate-in">
      <PageHeader title="Profile" description="Your account information and activity summary." />

      {/* Profile card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
            <Avatar className="h-20 w-20 border-2 border-border">
              <AvatarFallback className="bg-primary/10 text-primary text-xl font-semibold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 text-center sm:text-left">
              <h2 className="font-display text-xl font-bold text-foreground">{user.fullName}</h2>
              <p className="text-sm text-muted-foreground">{user.role}</p>
              <div className="mt-3 flex flex-col items-center gap-2 sm:flex-row sm:items-start">
                <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  {user.email}
                </span>
                {user.organization && (
                  <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground sm:ml-4">
                    <Building2 className="h-4 w-4" />
                    {user.organization}
                  </span>
                )}
                <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground sm:ml-4">
                  <Calendar className="h-4 w-4" />
                  Joined {new Date(user.createdAt).toLocaleDateString()}
                </span>
              </div>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link to="/settings">
                <Settings className="mr-2 h-4 w-4" />
                Edit settings
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.label}>
              <CardContent className="p-5">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${s.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <p className="mt-3 font-display text-2xl font-bold text-foreground">{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Demo data notice */}
      <Card className="border-warning/20">
        <CardHeader>
          <CardTitle className="text-base">Demo Data Notice</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed text-muted-foreground">
            This profile uses mock/demo data. When a backend is connected via VITE_API_BASE_URL,
            all data will be fetched from the API. Account information, analyses, and activity
            stats shown here are for demonstration purposes only.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
