import type { DocumentMetadata, AdminStats, HealthStatus, SourceCitation } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface ChatApiResponse {
  answer: string;
  sources: SourceCitation[];
  conversation_id: string;
  insufficient_context: boolean;
  error?: string | null;
}

export async function checkHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) throw new Error(`Health check failed with status ${res.status}`);
  return res.json();
}

export async function sendChatMessage(
  message: string,
  conversationId?: string | null,
  history?: Array<{ role: string; content: string }>
): Promise<ChatApiResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || undefined,
      history: history || [],
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Chat request failed (${res.status})`);
  }
  return res.json();
}

export async function adminLogin(username: string, password: string): Promise<{ access_token: string; username: string }> {
  const res = await fetch(`${API_BASE_URL}/api/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Invalid username or password');
  }
  return res.json();
}

export async function getAdminStats(token: string): Promise<AdminStats> {
  const res = await fetch(`${API_BASE_URL}/api/admin/stats`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch admin stats');
  }
  return res.json();
}

export async function listDocuments(token?: string | null): Promise<{ documents: DocumentMetadata[]; total_count: number }> {
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE_URL}/api/documents`, { headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch document list');
  }
  return res.json();
}

export async function uploadDocument(file: File, token: string): Promise<{ message: string; document_id: string; chunk_count: number }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Document upload failed');
  }
  return res.json();
}

export async function deleteDocument(documentId: string, token: string): Promise<{ message: string; document_id: string }> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Document deletion failed');
  }
  return res.json();
}

export async function reindexDocument(documentId: string, token: string): Promise<{ message: string; chunk_count: number }> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/reindex`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Reindexing failed');
  }
  return res.json();
}
