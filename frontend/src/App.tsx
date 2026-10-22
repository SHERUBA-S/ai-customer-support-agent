import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from './components/Navbar';
import { ChatMessage } from './components/Chat/ChatMessage';
import { ChatInput } from './components/Chat/ChatInput';
import { SuggestedQuestions } from './components/Chat/SuggestedQuestions';
import { FileUploadZone } from './components/Admin/FileUploadZone';
import { DocumentManager } from './components/Admin/DocumentManager';
import { StatsCard } from './components/Admin/StatsCard';
import { AdminLoginModal } from './components/Admin/AdminLoginModal';
import { KnowledgeBaseGuide } from './components/Admin/KnowledgeBaseGuide';
import { useAuth } from './context/AuthContext';
import { checkHealth, sendChatMessage, listDocuments, getAdminStats } from './services/api';
import type { ChatMessage as ChatMessageType, DocumentMetadata, AdminStats, HealthStatus } from './types';
import { Sparkles, AlertCircle, LogIn } from 'lucide-react';

export const App: React.FC = () => {
  const { isAuthenticated, token } = useAuth();
  const [currentTab, setCurrentTab] = useState<'chat' | 'documents' | 'analytics'>('chat');
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  // System & Stats State
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [docsLoading, setDocsLoading] = useState(false);

  // Chat State
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Initial Health & Documents Check
  const loadInitialData = async () => {
    try {
      const [h, docsRes] = await Promise.all([
        checkHealth().catch(() => null),
        listDocuments().catch(() => ({ documents: [], total_count: 0 })),
      ]);
      if (h) setHealth(h);
      if (docsRes?.documents) setDocuments(docsRes.documents);
    } catch (err) {
      console.warn('Backend not yet reachable:', err);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Fetch Documents & Admin Stats
  const loadAdminData = async () => {
    setDocsLoading(true);
    try {
      const [docsRes, statsRes] = await Promise.all([
        listDocuments(token),
        token ? getAdminStats(token) : null,
      ]);
      setDocuments(docsRes.documents);
      if (statsRes) setStats(statsRes);
      const h = await checkHealth().catch(() => null);
      if (h) setHealth(h);
    } catch (err) {
      console.error('Error fetching admin data:', err);
    } finally {
      setDocsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && token) {
      loadAdminData();
    }
  }, [isAuthenticated, token]);

  // Scroll to bottom on new message
  useEffect(() => {
    if (currentTab === 'chat') {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isChatLoading, currentTab]);

  // Send Chat Message
  const handleSendMessage = async (text: string) => {
    setChatError(null);

    // Append user message
    const userMsg: ChatMessageType = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setIsChatLoading(true);

    try {
      // Map history for backend context
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendChatMessage(text, conversationId, historyPayload);

      // Save conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Append assistant message
      const botMsg: ChatMessageType = {
        id: `b-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        insufficient_context: response.insufficient_context,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages([...newHistory, botMsg]);
    } catch (err: any) {
      setChatError(err.message || 'Failed to receive an answer from the support agent.');
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationId(null);
    setChatError(null);
  };

  const handleTabChange = (tab: 'chat' | 'documents' | 'analytics') => {
    setCurrentTab(tab);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={handleTabChange}
        onOpenLogin={() => setIsLoginModalOpen(true)}
        health={health}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* TAB 1: CUSTOMER CHAT */}
        {currentTab === 'chat' && (
          <div className="flex-1 flex flex-col bg-white border border-slate-200/90 rounded-2xl shadow-xs overflow-hidden min-h-[580px]">
            {/* Chat Messages Scroll Container */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col justify-center">
                  <SuggestedQuestions onSelectQuestion={handleSendMessage} />
                </div>
              ) : (
                <>
                  {messages.map((msg) => (
                    <ChatMessage key={msg.id} message={msg} />
                  ))}

                  {/* Loading indicator */}
                  {isChatLoading && (
                    <div className="flex items-start space-x-3 animate-fade-in">
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center shrink-0">
                        <Sparkles className="w-4 h-4 animate-spin" />
                      </div>
                      <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-white border border-slate-200 text-slate-500 text-xs flex items-center space-x-2 shadow-xs">
                        <div className="flex space-x-1">
                          <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                          <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                          <span className="w-1.5 h-1.5 bg-brand-500 rounded-full animate-bounce"></span>
                        </div>
                        <span className="font-medium text-slate-600">Retrieving company knowledge & formulating grounded answer...</span>
                      </div>
                    </div>
                  )}

                  {chatError && (
                    <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center space-x-2">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                      <span>{chatError}</span>
                    </div>
                  )}

                  <div ref={chatBottomRef} />
                </>
              )}
            </div>

            {/* Chat Input Bar */}
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isChatLoading}
              onClearChat={handleClearChat}
              hasMessages={messages.length > 0}
            />
          </div>
        )}

        {/* TAB 2: KNOWLEDGE BASE MANAGEMENT */}
        {currentTab === 'documents' && (
          <div className="space-y-6">
            {/* Guidelines Card explaining how users can add FAQs, policies, specs, and manuals */}
            <KnowledgeBaseGuide />

            {!isAuthenticated ? (
              <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 text-white rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm border border-slate-700/50">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-brand-500/30 text-brand-300 font-semibold text-[10px] uppercase tracking-wider">
                      Public Explorer
                    </span>
                    <h4 className="font-bold text-sm">Knowledge Base Documents</h4>
                  </div>
                  <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                    Browse all verified company policies currently parsed and embedded in ChromaDB. Authenticate as an administrator to upload new documents, delete, or re-index existing files.
                  </p>
                </div>
                <button
                  id="btn-admin-login-cta"
                  onClick={() => setIsLoginModalOpen(true)}
                  className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-white text-slate-900 font-semibold text-xs hover:bg-slate-100 transition-colors shrink-0 shadow-sm"
                >
                  <LogIn className="w-3.5 h-3.5 text-brand-600" />
                  <span>Admin Login</span>
                </button>
              </div>
            ) : (
              <FileUploadZone onUploadSuccess={loadAdminData} />
            )}

            <DocumentManager
              documents={documents}
              onRefresh={isAuthenticated && token ? loadAdminData : loadInitialData}
              isLoading={docsLoading}
              onRequireLogin={() => setIsLoginModalOpen(true)}
            />
          </div>
        )}

        {/* TAB 3: ANALYTICS & SYSTEM STATUS */}
        {currentTab === 'analytics' && (
          <StatsCard stats={stats} health={health} />
        )}
      </main>

      {/* Admin Login Modal */}
      <AdminLoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSuccess={() => {
          loadAdminData();
          setCurrentTab('documents');
        }}
      />
    </div>
  );
};
