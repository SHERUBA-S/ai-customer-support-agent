export interface SourceCitation {
  document_name: string;
  page_number?: number | null;
  relevant_excerpt: string;
  relevance_score: number;
  chunk_index?: number | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  insufficient_context?: boolean;
  timestamp: string;
}

export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  upload_date: string;
  status: 'indexed' | 'processing' | 'failed' | string;
  chunk_count: number;
  error_message?: string | null;
}

export interface AdminStats {
  total_documents: number;
  indexed_documents: number;
  failed_documents: number;
  total_chunks: number;
  llm_provider: string;
  embedding_provider: string;
  system_status: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  llm_provider: string;
  embedding_provider: string;
  total_documents: number;
  indexed_documents: number;
  total_indexed_chunks: number;
  vector_store: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
}
