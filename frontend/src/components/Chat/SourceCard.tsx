import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Sparkles, BookOpen } from 'lucide-react';
import type { SourceCitation } from '../../types';

interface SourceCardProps {
  citation: SourceCitation;
  index?: number;
}

export const SourceCard: React.FC<SourceCardProps> = ({ citation }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Convert relevance score to percentage
  const matchPct = Math.round(citation.relevance_score * 100);

  return (
    <div className="border border-slate-200/80 rounded-xl bg-white/70 shadow-xs hover:border-brand-300 hover:shadow-sm transition-all overflow-hidden text-xs">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between text-left hover:bg-slate-50/60 transition-colors"
      >
        <div className="flex items-center space-x-2 truncate pr-2">
          <div className="w-6 h-6 rounded-md bg-brand-50 text-brand-600 flex items-center justify-center shrink-0">
            <FileText className="w-3.5 h-3.5" />
          </div>
          <span className="font-medium text-slate-800 truncate" title={citation.document_name}>
            {citation.document_name}
          </span>
          {citation.page_number && (
            <span className="shrink-0 px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[10px]">
              Page {citation.page_number}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium text-[10px] border border-emerald-200/50">
            <Sparkles className="w-2.5 h-2.5" />
            <span>{matchPct}% match</span>
          </span>
          {isExpanded ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className="px-3.5 py-2.5 bg-slate-50/90 border-t border-slate-100 text-slate-600 leading-relaxed font-sans">
          <div className="flex items-center space-x-1 text-[11px] font-semibold text-slate-700 mb-1">
            <BookOpen className="w-3 h-3 text-brand-500" />
            <span>Retrieved Company Excerpt:</span>
          </div>
          <p className="bg-white p-2.5 rounded-lg border border-slate-200 text-slate-700 text-[11px] whitespace-pre-wrap select-text">
            {citation.relevant_excerpt}
          </p>
          {citation.chunk_index !== undefined && (
            <div className="mt-1.5 text-[10px] text-slate-400 text-right">
              Chunk Index: #{citation.chunk_index}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
