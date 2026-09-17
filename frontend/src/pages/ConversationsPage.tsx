import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MessageSquare, Plus, ArrowRight, Loader2 } from 'lucide-react';
import type { Conversation } from '@/models';
import { conversationService } from '@/services';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    setError('');
    conversationService
      .getConversations()
      .then(setConversations)
      .catch(() => setError('Failed to load conversations.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCreateNew = async () => {
    setCreating(true);
    try {
      const newConv = await conversationService.createConversation('New Conversation');
      navigate(`/conversations/${newConv.id}`);
    } catch {
      setError('Failed to create a new conversation.');
      setCreating(false);
    }
  };

  if (loading) return <LoadingState message="Loading conversations..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-6 animate-in">
      <PageHeader
        title="Conversations"
        description="Multi-turn conversations with environmental context awareness and scientific reasoning."
        actions={
          <Button size="sm" onClick={handleCreateNew} disabled={creating}>
            {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
            {creating ? 'Creating...' : 'New conversation'}
          </Button>
        }
      />

      {conversations.length === 0 ? (
        <EmptyState
          icon={<MessageSquare className="h-7 w-7 text-muted-foreground" />}
          title="No conversations yet"
          description="Start a conversation to ask environmental questions with full scientific context awareness."
          action={
            <Button size="sm" onClick={handleCreateNew} disabled={creating}>
              {creating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
              {creating ? 'Creating...' : 'New conversation'}
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {conversations.map((conv) => (
            <Link key={conv.id} to={`/conversations/${conv.id}`} className="block h-full">
              <Card className="h-full transition-all hover:shadow-md hover:border-primary/30">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                      <MessageSquare className="h-4 w-4 text-primary" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <h3 className="mt-3 font-display text-base font-semibold leading-snug text-foreground line-clamp-2">
                    {conv.title}
                  </h3>
                  <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{conv.messageCount} messages</span>
                    <span>•</span>
                    <span>{new Date(conv.updatedAt).toLocaleDateString()}</span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    <Badge variant="secondary" className="text-xs">
                      {conv.environmentalContext.known.length} known
                    </Badge>
                    {conv.environmentalContext.missing.length > 0 && (
                      <Badge variant="outline" className="text-xs border-warning/20 text-warning">
                        {conv.environmentalContext.missing.length} missing
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
export default ConversationsPage;
