"use client";

import { FormEvent, useMemo, useState } from "react";
import { supabase } from "../lib/supabaseClient";

interface ChatInterfaceProps {
  chartId: string;
  chartLabel: string;
}

interface ChatSource {
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

interface ChatProxyResponse {
  status: "ok";
  answer: string;
  sources: ChatSource[];
  experiment_id?: string | null;
  config_hash?: string | null;
  chunk_strategy_id?: string | null;
  generation_metadata?: Record<string, unknown>;
  citation_metadata?: Record<string, unknown>;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  experimentId?: string | null;
  chunkStrategyId?: string | null;
}

export function ChatInterface({ chartId, chartLabel }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const helperText = useMemo(
    () => `Hỏi trong ngữ cảnh lá số “${chartLabel}”. Câu trả lời sẽ đi kèm nguồn nếu pipeline tìm được context phù hợp.`,
    [chartLabel],
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuery = query.trim();
    if (!trimmedQuery || loading) {
      return;
    }

    setError(null);
    setLoading(true);
    setQuery("");

    const userMessage: ChatMessage = {
      id: makeMessageId("user"),
      role: "user",
      content: trimmedQuery,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const { data: sessionData } = await supabase.auth.getSession();
      const accessToken = sessionData.session?.access_token;
      if (!accessToken) {
        throw new Error("Bạn cần đăng nhập lại để đặt câu hỏi.");
      }

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ chart_id: chartId, query: trimmedQuery }),
      });

      const payload = await parseChatResponse(response);
      setMessages((current) => [
        ...current,
        {
          id: makeMessageId("assistant"),
          role: "assistant",
          content: payload.answer,
          sources: payload.sources,
          experimentId: payload.experiment_id ?? null,
          chunkStrategyId: payload.chunk_strategy_id ?? null,
        },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể gửi câu hỏi lúc này.";
      setError(message);
      setQuery(trimmedQuery);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="chat-section" aria-labelledby="chart-chat-title">
      <div className="chat-shell">
        <div className="chat-heading">
          <div>
            <p className="eyebrow">GraphRAG chat</p>
            <h2 id="chart-chat-title">Hỏi về lá số này</h2>
          </div>
          <span className="badge-pill">W5-FE-01 proxy</span>
        </div>

        <p className="chat-helper">{helperText}</p>

        <div className="chat-message-list" aria-live="polite">
          {messages.length === 0 && (
            <div className="chat-empty-state">
              <p>Gợi ý: “Cung Mệnh của lá số này nói gì?” hoặc “Các nguồn nào giải thích Thiên Di?”</p>
            </div>
          )}

          {messages.map((message) => (
            <article className={`chat-message ${message.role}`} key={message.id}>
              <div className="chat-message-label">{message.role === "user" ? "Bạn" : "Trợ lý Tử Vi"}</div>
              <p>{message.content}</p>
              {message.role === "assistant" && (
                <AssistantMessageMeta
                  chunkStrategyId={message.chunkStrategyId}
                  experimentId={message.experimentId}
                  sources={message.sources ?? []}
                />
              )}
            </article>
          ))}

          {loading && (
            <article className="chat-message assistant is-loading">
              <div className="chat-message-label">Trợ lý Tử Vi</div>
              <p>Đang truy vấn graph, vector và nguồn trích dẫn...</p>
            </article>
          )}
        </div>

        {error && <p className="error-message">{error}</p>}

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="chart-chat-query">
            Câu hỏi về lá số
          </label>
          <textarea
            id="chart-chat-query"
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Nhập câu hỏi về lá số hiện tại..."
            rows={3}
            value={query}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? "Đang hỏi..." : "Gửi câu hỏi"}
          </button>
        </form>
      </div>
    </section>
  );
}

function AssistantMessageMeta({
  chunkStrategyId,
  experimentId,
  sources,
}: {
  chunkStrategyId?: string | null;
  experimentId?: string | null;
  sources: ChatSource[];
}) {
  return (
    <div className="chat-meta-block">
      {(experimentId || chunkStrategyId) && (
        <div className="chat-run-meta">
          {experimentId && <span>Experiment: {experimentId}</span>}
          {chunkStrategyId && <span>Chunk: {chunkStrategyId}</span>}
        </div>
      )}

      <div className="chat-sources">
        <h3>Nguồn trích dẫn</h3>
        {sources.length === 0 ? (
          <p className="chat-source-empty">Pipeline chưa trả về nguồn cho câu trả lời này.</p>
        ) : (
          <div className="chat-source-grid">
            {sources.map((source, index) => (
              <article className="chat-source-card" key={source.chunk_id ?? source.chunk_hash ?? index}>
                <div className="chat-source-title">
                  <span>{source.citation_marker ? `[${source.citation_marker}]` : `S${index + 1}`}</span>
                  <strong>{source.source_name || source.source_id || "Nguồn Tử Vi"}</strong>
                </div>
                <p>{source.excerpt || "Không có excerpt."}</p>
                <div className="chat-source-footer">
                  {source.source_page ? <span>Trang {source.source_page}</span> : <span>Trang N/A</span>}
                  {typeof source.score === "number" && <span>Score {source.score.toFixed(3)}</span>}
                  {typeof source.confidence === "number" && <span>Conf {source.confidence.toFixed(2)}</span>}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

async function parseChatResponse(response: Response): Promise<ChatProxyResponse> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const message = extractErrorMessage(body) || response.statusText || "Chat proxy trả về lỗi.";
    throw new Error(message);
  }

  if (!isRecord(body) || typeof body.answer !== "string") {
    throw new Error("Chat proxy trả về dữ liệu không đúng định dạng.");
  }

  return {
    status: "ok",
    answer: body.answer,
    sources: Array.isArray(body.sources) ? (body.sources as ChatSource[]) : [],
    experiment_id: typeof body.experiment_id === "string" ? body.experiment_id : null,
    config_hash: typeof body.config_hash === "string" ? body.config_hash : null,
    chunk_strategy_id: typeof body.chunk_strategy_id === "string" ? body.chunk_strategy_id : null,
    generation_metadata: isRecord(body.generation_metadata) ? body.generation_metadata : {},
    citation_metadata: isRecord(body.citation_metadata) ? body.citation_metadata : {},
  };
}

function extractErrorMessage(body: unknown): string | null {
  if (!isRecord(body)) {
    return null;
  }
  if (typeof body.error === "string") return body.error;
  if (typeof body.detail === "string") return body.detail;
  return null;
}

function makeMessageId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}