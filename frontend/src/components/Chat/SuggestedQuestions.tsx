import React from 'react';
import { Truck, RotateCcw, Wrench, Shield, KeyRound, Sparkles } from 'lucide-react';

interface SuggestedQuestionsProps {
  onSelectQuestion: (question: string) => void;
}

const SAMPLE_PROMPTS = [
  {
    icon: RotateCcw,
    category: 'Returns & Refunds',
    question: 'What is the return window and how many days do I have?',
    color: 'text-amber-600 bg-amber-50 border-amber-200/60',
  },
  {
    icon: Truck,
    category: 'Shipping',
    question: 'What are the shipping options and delivery times?',
    color: 'text-blue-600 bg-blue-50 border-blue-200/60',
  },
  {
    icon: Wrench,
    category: 'Troubleshooting',
    question: 'My device will not power on, how do I perform a hard reset?',
    color: 'text-rose-600 bg-rose-50 border-rose-200/60',
  },
  {
    icon: Shield,
    category: 'Warranty (PDF)',
    question: 'How long is the limited hardware warranty and what does it cover?',
    color: 'text-emerald-600 bg-emerald-50 border-emerald-200/60',
  },
  {
    icon: KeyRound,
    category: 'Account & 2FA',
    question: 'How do I enable two-factor authentication and get emergency backup codes?',
    color: 'text-purple-600 bg-purple-50 border-purple-200/60',
  },
];

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ onSelectQuestion }) => {
  return (
    <div className="max-w-2xl mx-auto my-6 px-4 text-center">
      <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-xs font-semibold mb-3">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Grounded Knowledge Base Ready</span>
      </div>

      <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight mb-2">
        How can we help you today?
      </h2>
      <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
        Ask anything regarding company policies, delivery rates, hardware issues, or warranties.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
        {SAMPLE_PROMPTS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectQuestion(item.question)}
              className="p-3 rounded-xl border border-slate-200 bg-white hover:border-brand-400 hover:shadow-xs transition-all text-left flex items-start space-x-3 group"
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${item.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
                  {item.category}
                </div>
                <div className="text-xs font-medium text-slate-700 group-hover:text-brand-600 transition-colors line-clamp-2">
                  {item.question}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
