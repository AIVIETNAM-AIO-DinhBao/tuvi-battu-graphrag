export interface ChatSource {
  citation_marker?: string;
  chunk_id?: string;
  chunk_hash?: string;
  source_id?: string;
  source_name?: string;
  source_page?: number | string | null;
  excerpt?: string;
  score?: number | null;
  confidence?: number | null;
  retrieval_paths?: string[];
}

export interface ChatProxyResponse {
  status: "ok";
  answer: string;
  sources: ChatSource[];
  experiment_id?: string | null;
  config_hash?: string | null;
  chunk_strategy_id?: string | null;
  generation_metadata?: Record<string, unknown>;
  citation_metadata?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
  sources?: ChatSource[];
  experimentId?: string | null;
  configHash?: string | null;
  chunkStrategyId?: string | null;
  generationMetadata?: Record<string, unknown>;
  citationMetadata?: Record<string, unknown>;
}