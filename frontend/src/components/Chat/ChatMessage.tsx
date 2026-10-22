import React, { useState } from 'react';
import { Bot, User, Copy, Check, AlertCircle, Bookmark } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../../types';
import { SourceCard } from './SourceCard';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`flex items-start max-w-2xl sm:max-w-3xl space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-xs ${
            isUser
              ? 'bg-slate-800 text-white'
              : 'bg-gradient-to-tr from-brand-600 to-indigo-600 text-white'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message Bubble */}
        <div className="flex-1 space-y-2">
          <div
            className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              isUser
                ? 'bg-slate-900 text-white rounded-tr-none shadow-xs'
                : message.insufficient_context
                ? 'bg-amber-50/80 border border-amber-200 text-amber-950 rounded-tl-none'
                : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-none shadow-xs'
            }`}
          >
            {/* Insufficient Context Alert Banner if applicable */}
            {!isUser && message.insufficient_context && (
              <div className="flex items-center space-x-1.5 text-xs font-semibold text-amber-800 mb-2 pb-1.5 border-b border-amber-200/60">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                <span>Information Not In Company Knowledge Base</span>
              </div>
            )}

            {/* Answer Content */}
            <div className="whitespace-pre-wrap break-words">{message.content}</div>

            {/* Bottom Actions for AI Message */}
            {!isUser && (
              <div className="flex items-center justify-between pt-2 mt-2 border-t border-slate-100 text-[11px] text-slate-400">
                <span>{message.timestamp}</span>
                <button
                  onClick={handleCopy}
                  className="flex items-center space-x-1 px-2 py-0.5 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                  title="Copy answer to clipboard"
                >
                  {copied ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-600 font-medium">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Source Citations Section */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="pt-1 space-y-1.5">
              <div className="flex items-center space-x-1.5 text-[11px] font-semibold text-slate-500 px-1">
                <Bookmark className="w-3 h-3 text-brand-600" />
                <span>Verified Sources ({message.sources.length})</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {message.sources.map((citation, idx) => (
                  <SourceCard key={`${citation.document_name}-${idx}`} citation={citation} index={idx} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
