import React from 'react';
import { Files, CheckCircle, AlertTriangle, Cpu, HardDrive, Activity } from 'lucide-react';
import type { AdminStats, HealthStatus } from '../../types';

interface StatsCardProps {
  stats: AdminStats | null;
  health: HealthStatus | null;
}

export const StatsCard: React.FC<StatsCardProps> = ({ stats, health }) => {
  const totalDocs = stats?.total_documents ?? health?.total_documents ?? 0;
  const indexedDocs = stats?.indexed_documents ?? health?.indexed_documents ?? 0;
  const failedDocs = stats?.failed_documents ?? 0;
  const totalChunks = stats?.total_chunks ?? health?.total_indexed_chunks ?? 0;
  const llm = stats?.llm_provider ?? health?.llm_provider ?? 'mock';
  const embed = stats?.embedding_provider ?? health?.embedding_provider ?? 'local';

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Documents */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Files className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalDocs}</div>
            <div className="text-xs font-medium text-slate-500">Total Documents</div>
          </div>
        </div>

        {/* Successfully Indexed */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{indexedDocs}</div>
            <div className="text-xs font-medium text-slate-500">Indexed In ChromaDB</div>
          </div>
        </div>

        {/* Failed Documents */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{failedDocs}</div>
            <div className="text-xs font-medium text-slate-500">Failed Processing Jobs</div>
          </div>
        </div>

        {/* Total Chunks */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <HardDrive className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalChunks}</div>
            <div className="text-xs font-medium text-slate-500">Vector Embeddings</div>
          </div>
        </div>
      </div>

      {/* System Infrastructure Details Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <h4 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-brand-600" />
          <span>Active RAG Pipeline Configuration</span>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs text-slate-500 mb-1">
              <Cpu className="w-4 h-4 text-indigo-600" />
              <span>LLM Engine Provider</span>
            </div>
            <div className="text-sm font-bold text-slate-800 uppercase tracking-wide">
              {llm === 'mock' ? 'Grounded Dev Engine (Offline)' : llm}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              {llm === 'mock'
                ? 'Deterministic zero-hallucination local mode. Plug in OpenAI/Gemini keys anytime.'
                : `Connected to ${llm} generative API.`}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs text-slate-500 mb-1">
              <HardDrive className="w-4 h-4 text-purple-600" />
              <span>Embedding Vector Model</span>
            </div>
            <div className="text-sm font-bold text-slate-800 uppercase tracking-wide">
              {embed === 'local' ? 'Local Semantic Hash (384-Dim)' : embed}
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Zero-download normalized n-gram semantic vector space.
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs text-slate-500 mb-1">
              <CheckCircle className="w-4 h-4 text-emerald-600" />
              <span>Vector Database</span>
            </div>
            <div className="text-sm font-bold text-slate-800">
              ChromaDB (Persistent HNSW)
            </div>
            <div className="text-[11px] text-slate-500 mt-1">
              Stored locally under <code className="bg-slate-200 px-1 rounded">/data/chroma_db</code> with SQLite backend.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
