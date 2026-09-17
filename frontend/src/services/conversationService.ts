import type { Conversation, ConversationMessage, EnvironmentalContext } from '@/models';
import { request, mockDelay, API_BASE_URL } from './http';
import { mockConversations } from '@/data/conversations';

export interface SendMessageResponse {
  conversation_id: string;
  response: string;
  message?: string;
  response_type: string;
  clarification_required: boolean;
  clarification_question?: string;
  environmental_context: EnvironmentalContext;
  recommendations?: any[];
  evidence?: any[];
  limitations?: string[];
  llm_available: boolean;
  llm_used?: string;
}

export interface ExtendedConversationMessage extends ConversationMessage {
  responseType?: string;
  clarificationRequired?: boolean;
  clarificationQuestion?: string;
  environmentalContext?: EnvironmentalContext;
  recommendations?: any[];
  evidence?: any[];
  limitations?: string[];
  llmAvailable?: boolean;
  llmUsed?: string;
}

export const conversationService = {
  async getConversations(): Promise<Conversation[]> {
    if (!API_BASE_URL) {
      return mockDelay(mockConversations);
    }
    return request<Conversation[]>('/api/conversations');
  },

  async getConversation(id: string): Promise<Conversation> {
    if (!API_BASE_URL) {
      const conv = mockConversations.find((c) => c.id === id) || mockConversations[0];
      return mockDelay(conv);
    }
    return request<any>(`/api/conversations/${id}`).then((c) => ({
      ...c,
      environmentalContext: c.environmentalContext || c.environmental_context || { known: [], missing: [] },
    }));
  },

  async sendMessage(
    conversationId: string,
    content: string,
    signal?: AbortSignal,
  ): Promise<ExtendedConversationMessage> {
    if (!API_BASE_URL) {
      const mockReply: ExtendedConversationMessage = {
        id: 'msg-' + Date.now(),
        role: 'assistant',
        content:
          'Based on the environmental data available, I can provide an assessment. The watershed shows moderate health with key areas for improvement.',
        timestamp: new Date().toISOString(),
        llmAvailable: true,
      };
      return mockDelay(mockReply, 800);
    }

    const res = await request<SendMessageResponse>('/api/conversations/message', {
      method: 'POST',
      body: JSON.stringify({
        conversation_id: conversationId,
        message: content,
      }),
      signal,
    });

    const evidenceRefs = (res.evidence || [])
      .map((e: any) => e.chunk_id || e.document_id)
      .filter(Boolean);

    return {
      id: 'msg-' + Date.now(),
      role: 'assistant',
      content: res.response || res.message || '',
      timestamp: new Date().toISOString(),
      evidenceRefs,
      responseType: res.response_type,
      clarificationRequired: res.clarification_required,
      clarificationQuestion: res.clarification_question,
      environmentalContext: (res as any).environmentalContext || res.environmental_context || { known: [], missing: [] },
      recommendations: res.recommendations || [],
      evidence: res.evidence || [],
      limitations: res.limitations || [],
      llmAvailable: res.llm_available,
      llmUsed: res.llm_used,
    };
  },

  async createConversation(title: string = "New Conversation"): Promise<Conversation> {
    if (!API_BASE_URL) {
      const newConv: Conversation = {
        id: 'conv-' + Date.now(),
        title,
        messages: [],
        environmentalContext: { known: [], missing: [] },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 0,
      };
      return mockDelay(newConv);
    }
    return request<Conversation>('/api/conversations', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  },
};
