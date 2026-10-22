import React, { useState } from 'react';
import { BookOpen, FileText, HelpCircle, CheckCircle2, ChevronDown, ChevronUp, Layers } from 'lucide-react';

export const KnowledgeBaseGuide: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-slate-50/60 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center shrink-0">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
              <span>Knowledge Base Guidelines: Adding FAQs, Policies, Product Info & Manuals</span>
              <span className="px-1.5 py-0.2 rounded bg-brand-100 text-brand-700 font-semibold text-[10px]">Best Practices</span>
            </h4>
            <p className="text-[11px] text-slate-500">
              Learn how to prepare company documents for optimal RAG retrieval and citation accuracy.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1 text-xs text-slate-400">
          <span className="hidden sm:inline text-[11px] font-medium">{isOpen ? 'Hide Guide' : 'View Guide'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 pt-2 border-t border-slate-100 space-y-4 text-xs text-slate-600 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Guide Card 1: FAQs */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold">
                <HelpCircle className="w-4 h-4 text-blue-600" />
                <span>Company FAQs</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Format each question as a clear header (`### Question`) followed by a concise, authoritative answer. Avoid vague answers so the vector embedder can match questions cleanly.
              </p>
            </div>

            {/* Guide Card 2: Policies */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold">
                <FileText className="w-4 h-4 text-emerald-600" />
                <span>Policies & Terms</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                State quantitative rules clearly (e.g., "30-day return window", "1-year warranty", "$6.50 return fee"). These specific details allow the RAG agent to answer without ambiguity.
              </p>
            </div>

            {/* Guide Card 3: Product Info */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold">
                <Layers className="w-4 h-4 text-purple-600" />
                <span>Product Specifications</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Group features by product model name. Include technical specifications, compatible accessories, input voltages, and operating temperature ranges.
              </p>
            </div>

            {/* Guide Card 4: Support Manuals */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
              <div className="flex items-center space-x-2 text-slate-900 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-amber-600" />
                <span>Troubleshooting Manuals</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Provide numbered, sequential steps for common problems (e.g., hard reset, pairing, LED error codes). The agent cites the exact page number and excerpt for customers.
              </p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-brand-50/60 border border-brand-200/70 text-[11px] text-brand-900 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="font-semibold text-brand-950">Supported Formats:</span> PDF (extractable text, multi-page), Markdown (`.md`), and Plain Text (`.txt`).
              <span className="block text-slate-500">Maximum file size: 15MB. All documents are automatically chunked with overlap and preserved in ChromaDB.</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
