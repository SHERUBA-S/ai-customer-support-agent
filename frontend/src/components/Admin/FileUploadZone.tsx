import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

interface FileUploadZoneProps {
  onUploadSuccess: () => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({ onUploadSuccess }) => {
  const { token } = useAuth();
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileProcess = async (file: File) => {
    if (!token) return;
    setStatusMessage(null);

    // Validate extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['pdf', 'txt', 'md', 'markdown'].includes(ext)) {
      setStatusMessage({
        type: 'error',
        text: `File type '.${ext}' not supported. Please upload PDF, TXT, or Markdown documents.`,
      });
      return;
    }

    // Validate size (15 MB)
    if (file.size > 15 * 1024 * 1024) {
      setStatusMessage({
        type: 'error',
        text: 'File exceeds maximum permitted limit of 15 MB.',
      });
      return;
    }

    setUploading(true);
    try {
      const res = await uploadDocument(file, token);
      setStatusMessage({
        type: 'success',
        text: `"${file.name}" indexed successfully into ${res.chunk_count} vector chunks!`,
      });
      onUploadSuccess();
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      setStatusMessage({
        type: 'error',
        text: err.message || 'Failed to upload and index document.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
      <h3 className="text-sm font-bold text-slate-800 mb-1 flex items-center space-x-2">
        <UploadCloud className="w-4 h-4 text-brand-600" />
        <span>Upload & Ingest Company Document</span>
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        Supports PDF, TXT, and Markdown files up to 15MB. Text will be chunked, embedded, and indexed into ChromaDB.
      </p>

      {/* Drop Target */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-brand-500 bg-brand-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-brand-400 hover:bg-slate-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,.markdown"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileProcess(e.target.files[0]);
            }
          }}
        />

        {uploading ? (
          <div className="flex flex-col items-center justify-center space-y-2 py-2">
            <Loader2 className="w-8 h-8 text-brand-600 animate-spin" />
            <span className="text-xs font-semibold text-slate-700">
              Extracting text, chunking, and generating vector embeddings...
            </span>
            <span className="text-[11px] text-slate-400">Storing in ChromaDB collection</span>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center space-y-2">
            <div className="w-12 h-12 rounded-full bg-brand-50 text-brand-600 flex items-center justify-center">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div className="text-xs font-semibold text-slate-800">
              Drag & drop your document here, or <span className="text-brand-600 underline">browse files</span>
            </div>
            <div className="flex items-center space-x-2 text-[11px] text-slate-400">
              <span className="px-2 py-0.5 bg-slate-100 rounded">PDF</span>
              <span className="px-2 py-0.5 bg-slate-100 rounded">TXT</span>
              <span className="px-2 py-0.5 bg-slate-100 rounded">MD</span>
              <span>• Max 15MB</span>
            </div>
          </div>
        )}
      </div>

      {/* Status Alert Banner */}
      {statusMessage && (
        <div
          className={`mt-4 p-3 rounded-xl border flex items-center space-x-2 text-xs ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}
    </div>
  );
};
