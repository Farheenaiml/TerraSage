import { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Send,
  Loader2,
  CheckCircle2,
  HelpCircle,
  BookOpen,
  ArrowLeft,
  Sprout,
  AlertTriangle,
  Info,
  Layers,
  Sparkles,
} from 'lucide-react';
import { conversationService, type ExtendedConversationMessage } from '@/services/conversationService';
import type { Conversation, ConversationMessage } from '@/models';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { cn } from '@/lib/utils';

const EXAMPLE_PROMPTS = [
  {
    title: '🌾 Semi-Arid Monoculture Wheat',
    text: 'Soil organic carbon: 0.3%, rainfall: low, crop: monoculture wheat, region: semi-arid',
  },
  {
    title: '🍇 Nashik Farm Biodiversity',
    text: 'My farm is in Nashik, Maharashtra and I grow grapes',
  },
  {
    title: '📉 Biodiversity Decline Clarification',
    text: 'Biodiversity is declining on my land',
  },
  {
    title: '🌱 Agroforestry & Soil Health',
    text: 'What agroforestry practices increase soil organic carbon and microbial diversity?',
  },
];

export function ConversationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const load = () => {
    setLoading(true);
    setError('');
    if (!id) return;
    if (id === 'new') {
      setConversation({
        id: 'new',
        title: 'New Environmental Consultation',
        messages: [],
        environmentalContext: { known: [], missing: [] },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 0,
      });
      setLoading(false);
      return;
    }
    conversationService
      .getConversation(id)
      .then(setConversation)
      .catch(() => setError('Failed to load conversation.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages.length]);

  const handleSend = async (overrideText?: string) => {
    const textToSend = (overrideText ?? input).trim();
    if (!textToSend || sending) return;
    setSending(true);

    let activeId = id;
    let currentConv = conversation;

    // If starting from /conversations/new, create in backend first
    if (activeId === 'new' || !currentConv) {
      try {
        const titleSnippet = textToSend.length > 35 ? textToSend.slice(0, 32) + '...' : textToSend;
        const created = await conversationService.createConversation(titleSnippet);
        activeId = created.id;
        currentConv = {
          ...created,
          messages: [],
          environmentalContext: { known: [], missing: [] },
        };
        navigate(`/conversations/${created.id}`, { replace: true });
      } catch {
        setError('Failed to create conversation on backend.');
        setSending(false);
        return;
      }
    }

    const userMsg: ConversationMessage = {
      id: 'msg-tmp-' + Date.now(),
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString(),
    };

    setConversation({
      ...currentConv,
      id: activeId!,
      messages: [...currentConv.messages, userMsg],
      messageCount: currentConv.messageCount + 1,
    });
    setInput('');

    try {
      const reply = await conversationService.sendMessage(activeId!, textToSend);
      setConversation((prev) => {
        if (!prev) return prev;
        const updatedContext = reply.environmentalContext || prev.environmentalContext;
        return {
          ...prev,
          environmentalContext: updatedContext,
          messages: [...prev.messages, reply],
          messageCount: prev.messageCount + 1,
        };
      });
    } catch (err) {
      const errorMsg: ConversationMessage = {
        id: 'msg-err-' + Date.now(),
        role: 'assistant',
        content: '⚠️ The request encountered a delay. All site context is preserved. Please click Send to retry.',
        timestamp: new Date().toISOString(),
      };
      setConversation((prev) => prev ? { ...prev, messages: [...prev.messages, errorMsg] } : prev);
    } finally {
      setSending(false);
    }
  };

  if (loading) return <LoadingState message="Loading conversation..." />;
  if (!conversation)
    return <ErrorState message={error || 'Conversation not found.'} onRetry={load} />;

  return (
    <div className="flex flex-col gap-4 lg:flex-row animate-in" style={{ minHeight: 'calc(100vh - 8rem)' }}>
      {/* Chat */}
      <div className="flex flex-1 flex-col">
        <div className="mb-4 flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild className="h-8 w-8">
            <Link to="/conversations">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="font-display text-xl font-bold text-foreground">{conversation.title}</h1>
            <p className="text-xs text-muted-foreground">
              {conversation.messageCount} messages • {conversation.id === 'new' ? 'Draft' : `Started ${new Date(conversation.createdAt).toLocaleDateString()}`}
            </p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-4 overflow-y-auto rounded-xl border border-border bg-card p-4 scrollbar-thin">
          {conversation.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-4 py-12 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <Sprout className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-foreground">AI Environmental Scientist Consultation</h3>
                <p className="mt-1 max-w-md text-xs text-muted-foreground">
                  Ask multi-metric questions about your land, soil health, regional climate, or biodiversity loss. Every answer is grounded in scientific evidence from FAO, IPCC, and real data providers.
                </p>
              </div>

              <div className="mt-4 grid w-full max-w-xl gap-2 sm:grid-cols-2 text-left">
                {EXAMPLE_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSend(prompt.text)}
                    className="flex flex-col gap-1 rounded-lg border border-border/70 bg-muted/30 p-3 transition-all hover:bg-muted/80 hover:border-primary/40 text-left"
                  >
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-primary">
                      <Sparkles className="h-3 w-3" />
                      <span>{prompt.title}</span>
                    </div>
                    <span className="text-[11px] text-muted-foreground line-clamp-2">{prompt.text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            conversation.messages.map((msg) => {
              const ext = msg as ExtendedConversationMessage;
              const isClarification = ext.responseType === 'clarification' || ext.clarificationRequired;
              const isLlmUnavailable = ext.llmAvailable === false;

              return (
                <div
                  key={msg.id}
                  className={cn('flex flex-col', msg.role === 'user' ? 'items-end' : 'items-start')}
                >
                  <div
                    className={cn(
                      'max-w-[85%] rounded-xl px-4 py-3',
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : isClarification
                        ? 'border border-warning/40 bg-warning/10 text-foreground'
                        : 'bg-muted text-foreground',
                    )}
                  >
                    {isClarification && (
                      <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-warning">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        <span>Clarification Needed</span>
                      </div>
                    )}

                    {msg.role === 'user' ? (
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                    ) : (
                      <FormattedMessage content={msg.content} />
                    )}

                    {isLlmUnavailable && (
                      <div className="mt-3 rounded border border-border/80 bg-background/80 p-2.5 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1.5 font-medium text-foreground">
                          <Info className="h-3.5 w-3.5 text-muted-foreground" />
                          <span>Deterministic Pipeline Operating in Direct Mode</span>
                        </div>
                        <p className="mt-1 text-[11px] leading-relaxed">
                          Scientific reasoning engine, multi-metric analysis, and evidence retrieval are operating normally.
                        </p>
                      </div>
                    )}

                    {ext.recommendations && ext.recommendations.length > 0 && (
                      <div className="mt-3 space-y-1.5 border-t border-border/60 pt-2.5">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                          <Layers className="h-3.5 w-3.5 text-primary" />
                          <span>Generated Recommendations ({ext.recommendations.length})</span>
                        </div>
                        {ext.recommendations.map((rec: any, idx: number) => (
                          <div key={idx} className="flex items-center justify-between rounded bg-background/60 px-2.5 py-1.5 text-xs">
                            <span className="font-medium text-foreground">{rec.title}</span>
                            <Badge variant="outline" className="text-[10px]">{rec.category}</Badge>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span className="text-[10px] opacity-60">
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      {msg.evidenceRefs && msg.evidenceRefs.length > 0 && (
                        <span className="inline-flex items-center gap-1 rounded bg-background/40 px-1.5 py-0.5 text-[10px] opacity-80">
                          <BookOpen className="h-3 w-3" />
                          {msg.evidenceRefs.length} evidence citations
                        </span>
                      )}
                      {ext.llmUsed && (
                        <span className="inline-flex items-center gap-1 text-[10px] opacity-60">
                          Engine: {ext.llmUsed}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
          {sending && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-xl bg-muted px-4 py-3">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Running environmental pipeline...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="mt-4 flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about soil, climate, biodiversity, or describe your site (e.g., 'Soil organic carbon: 0.3%, low rainfall, monoculture wheat')..."
            rows={2}
            className="resize-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <Button onClick={() => handleSend()} disabled={!input.trim() || sending} size="icon" className="h-auto">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Environmental Context Panel */}
      <div className="w-full shrink-0 lg:w-80">
        <Card className="sticky top-20">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Environmental Context</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-success">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Known variables
              </p>
              <div className="space-y-2">
                {!conversation.environmentalContext?.known || conversation.environmentalContext.known.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No variables known yet. Provide site details or location.</p>
                ) : (
                  conversation.environmentalContext.known.map((k, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md bg-muted/50 px-2.5 py-1.5">
                      <span className="text-xs text-muted-foreground">
                        {k.category}: {k.field}
                      </span>
                      <span className="text-xs font-medium text-foreground">{k.value}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="border-t border-border pt-3">
              <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-warning">
                <HelpCircle className="h-3.5 w-3.5" />
                Missing variables
              </p>
              <div className="space-y-2">
                {!conversation.environmentalContext?.missing || conversation.environmentalContext.missing.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No missing variables.</p>
                ) : (
                  conversation.environmentalContext.missing.map((m, i) => (
                    <div key={i} className="rounded-md border border-warning/20 bg-warning/5 px-2.5 py-1.5">
                      <Badge variant="outline" className="mb-1 text-[10px] border-warning/20 text-warning">
                        {m.category}
                      </Badge>
                      <p className="text-xs text-muted-foreground">{m.field}</p>
                      <p className="mt-0.5 text-[11px] leading-relaxed text-muted-foreground/80">{m.question}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


function FormattedMessage({ content }: { content: string }) {
  const lines = content.split('\n');
  return (
    <div className="space-y-1.5 text-sm leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        const isHeader = trimmed.startsWith('**[') || (trimmed.startsWith('**') && trimmed.endsWith('**') && trimmed.length < 80);

        const parts = line.split(/(\**.*?\**)/g);
        const formattedParts = parts.map((part, pIdx) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={pIdx} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
          }
          return part;
        });

        if (trimmed.startsWith('•') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2">
              <span className="text-primary mt-0.5 text-xs">•</span>
              <div className="flex-1">{formattedParts}</div>
            </div>
          );
        }

        if (isHeader) {
          return (
            <div key={idx} className="font-display font-bold text-foreground text-sm pt-1">
              {formattedParts}
            </div>
          );
        }

        return <div key={idx}>{formattedParts}</div>;
      })}
    </div>
  );
}

export default ConversationDetailPage;
