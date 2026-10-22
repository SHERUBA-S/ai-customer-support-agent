import React, { useState } from 'react';
import { FileText, Trash2, RefreshCw, AlertTriangle, CheckCircle, Clock, Database, Loader2 } from 'lucide-react';
import type { DocumentMetadata } from '../../types';
import { deleteDocument, reindexDocument } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

interface DocumentManagerProps {
  documents: DocumentMetadata[];
  onRefresh: () => void;
  isLoading: boolean;
  onRequireLogin?: () => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  documents,
  onRefresh,
  isLoading,
  onRequireLogin,
}) => {
  const { token, isAuthenticated } = useAuth();
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleDelete = async (doc: DocumentMetadata) => {
    if (!isAuthenticated || !token) {
      onRequireLogin?.();
      return;
    }
    if (!window.confirm(`Are you sure you want to permanently delete "${doc.filename}" and purge all of its vectors from ChromaDB?`)) {
      return;
    }

    setActionInProgress(doc.document_id);
    setFeedback(null);
    try {
      await deleteDocument(doc.document_id, token);
      setFeedback(`"${doc.filename}" and its associated vectors deleted.`);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to delete document');
    } finally {
      setActionInProgress(null);
    }
  };

  const handleReindex = async (doc: DocumentMetadata) => {
    if (!isAuthenticated || !token) {
      onRequireLogin?.();
      return;
    }
    setActionInProgress(doc.document_id);
    setFeedback(null);
    try {
      const res = await reindexDocument(doc.document_id, token);
      setFeedback(`"${doc.filename}" reindexed successfully into ${res.chunk_count} chunks.`);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to reindex document');
    } finally {
      setActionInProgress(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
            <Database className="w-4 h-4 text-brand-600" />
            <span>Indexed Knowledge Base Documents ({documents.length})</span>
          </h3>
          <p className="text-xs text-slate-500">
            Real documents currently parsed and embedded in the persistent vector store.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {feedback && (
        <div className="mx-6 mt-4 p-2.5 bg-blue-50 border border-blue-200 rounded-xl text-blue-800 text-xs flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{feedback}</span>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-sm">
          No documents uploaded yet. Upload your first PDF, TXT, or MD above.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold text-[10px]">
              <tr>
                <th className="px-6 py-3">Document</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Chunks</th>
                <th className="px-4 py-3">Size</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {documents.map((doc) => {
                const isWorking = actionInProgress === doc.document_id;
                return (
                  <tr key={doc.document_id} className="hover:bg-slate-50/60 transition-colors">
                    {/* Filename */}
                    <td className="px-6 py-3.5 font-medium text-slate-800 flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center shrink-0">
                        <FileText className="w-4 h-4" />
                      </div>
                      <span className="truncate max-w-xs sm:max-w-md font-semibold" title={doc.filename}>
                        {doc.filename}
                      </span>
                    </td>

                    {/* File Type */}
                    <td className="px-4 py-3.5">
                      <span className="uppercase font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        .{doc.file_type}
                      </span>
                    </td>

                    {/* Chunk Count */}
                    <td className="px-4 py-3.5">
                      <span className="font-semibold text-slate-900 bg-brand-50 text-brand-700 px-2 py-0.5 rounded-full text-[11px]">
                        {doc.chunk_count} chunks
                      </span>
                    </td>

                    {/* File Size */}
                    <td className="px-4 py-3.5 text-slate-500 font-mono text-[11px]">
                      {formatFileSize(doc.file_size_bytes)}
                    </td>

                    {/* Status Badge */}
                    <td className="px-4 py-3.5">
                      {doc.status === 'indexed' ? (
                        <span className="inline-flex items-center space-x-1 text-emerald-700 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full text-[10px] font-medium">
                          <CheckCircle className="w-3 h-3 text-emerald-600" />
                          <span>Indexed</span>
                        </span>
                      ) : doc.status === 'processing' ? (
                        <span className="inline-flex items-center space-x-1 text-blue-700 bg-blue-50 border border-blue-200/60 px-2 py-0.5 rounded-full text-[10px] font-medium">
                          <Clock className="w-3 h-3 text-blue-600 animate-pulse" />
                          <span>Processing</span>
                        </span>
                      ) : (
                        <span
                          className="inline-flex items-center space-x-1 text-rose-700 bg-rose-50 border border-rose-200/60 px-2 py-0.5 rounded-full text-[10px] font-medium"
                          title={doc.error_message || 'Indexing failed'}
                        >
                          <AlertTriangle className="w-3 h-3 text-rose-600" />
                          <span>Failed</span>
                        </span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-3.5 text-right space-x-2">
                      <button
                        onClick={() => handleReindex(doc)}
                        disabled={isWorking}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-brand-600 hover:bg-brand-50 border border-slate-200 transition-colors"
                        title="Re-index document into ChromaDB"
                      >
                        {isWorking ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <RefreshCw className="w-3.5 h-3.5" />
                        )}
                      </button>

                      <button
                        onClick={() => handleDelete(doc)}
                        disabled={isWorking}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition-colors"
                        title="Delete document and purge vectors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
