import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  onClearChat: () => void;
  hasMessages: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  onClearChat,
  hasMessages,
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading) return;
    onSendMessage(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <div className="border-t border-slate-200 bg-white/80 backdrop-blur-md p-3 sm:p-4">
      <div className="max-w-4xl mx-auto flex items-end space-x-2">
        {/* Clear chat button */}
        {hasMessages && (
          <button
            onClick={onClearChat}
            className="p-2.5 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition-colors shrink-0"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}

        {/* Input box */}
        <div className="flex-1 relative rounded-2xl border border-slate-300 bg-white shadow-xs focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/20 transition-all flex items-end">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="Ask a question about shipping, refunds, hardware, or policies... (Enter to send)"
            className="w-full py-3 pl-4 pr-12 text-sm text-slate-800 placeholder-slate-400 bg-transparent resize-none focus:outline-none max-h-32 min-h-[46px]"
          />

          <button
            onClick={() => handleSubmit()}
            disabled={!text.trim() || isLoading}
            className={`absolute right-2 bottom-2 p-2 rounded-xl transition-all ${
              text.trim() && !isLoading
                ? 'bg-brand-600 text-white hover:bg-brand-700 shadow-sm'
                : 'text-slate-300 bg-slate-100 cursor-not-allowed'
            }`}
            title="Send message (Enter)"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto mt-2 flex items-center justify-between text-[11px] text-slate-400 px-1">
        <span>Grounded in official company documents only. No hallucinations.</span>
        <span className="hidden sm:inline-flex items-center space-x-1">
          <span>Press</span>
          <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] text-slate-600 font-mono">Enter ↵</kbd>
          <span>to send</span>
        </span>
      </div>
    </div>
  );
};
