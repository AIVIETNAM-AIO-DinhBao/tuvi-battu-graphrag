"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import {
  SourceCitationPanel,
  getSourceKey,
  getSourceMarker,
} from "./SourceCitationPanel";
import { ChatMessage, ChatProxyResponse, ChatSource } from "../lib/chatTypes";
import { supabase } from "../lib/supabaseClient";

interface ChatInterfaceProps {
  chartId: string;
  chartLabel: string;
}

interface ChatSessionRow {
  id: string;
  messages: unknown;
}

export function ChatInterface({ chartId, chartLabel }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFailedQuery, setLastFailedQuery] = useState<string | null>(null);
  const [selectedSourceByMessage, setSelectedSourceByMessage] = useState<Record<string, string | null>>({});

  const helperText = useMemo(
    () => `Hỏi trong ngữ cảnh lá số “${chartLabel}”. Lịch sử chat được lưu theo từng lá số và câu trả lời sẽ đi kèm nguồn nếu pipeline tìm được context phù hợp.`,
    [chartLabel],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadChatSession() {
      setHistoryLoading(true);
      setError(null);
      setLastFailedQuery(null);
      setSessionId(null);
      setMessages([]);

      try {
        const { data: sessionData } = await supabase.auth.getSession();
        const user = sessionData.session?.user;
        if (!user) {
          throw new Error("Bạn cần đăng nhập lại để tải lịch sử chat.");
        }

        const { data: existingSession, error: fetchError } = await supabase
          .from("chat_sessions")
          .select("id,messages")
          .eq("la_so_id", chartId)
          .maybeSingle();

        if (fetchError) {
          throw new Error(`Không thể tải lịch sử chat: ${fetchError.message}`);
        }

        if (cancelled) return;

        if (existingSession) {
          const row = existingSession as ChatSessionRow;
          setSessionId(row.id);
          setMessages(normalizeMessages(row.messages));
          return;
        }

        const { data: newSession, error: insertError } = await supabase
          .from("chat_sessions")
          .insert({
            user_id: user.id,
            la_so_id: chartId,
            title: `Chat: ${chartLabel}`,
            messages: [],
          })
          .select("id,messages")
          .single();

        if (insertError) {
          throw new Error(`Không thể tạo lịch sử chat: ${insertError.message}`);
        }

        if (cancelled) return;
        const row = newSession as ChatSessionRow;
        setSessionId(row.id);
        setMessages(normalizeMessages(row.messages));
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Không thể tải lịch sử chat.");
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      }
    }

    if (chartId) {
      loadChatSession();
    }

    return () => {
      cancelled = true;
    };
  }, [chartId, chartLabel]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await submitQuestion(query);
  }

  async function submitQuestion(rawQuery: string) {
    const trimmedQuery = rawQuery.trim();
    if (!trimmedQuery || loading || historyLoading) {
      return;
    }

    setError(null);
    setLastFailedQuery(null);
    setLoading(true);
    setQuery("");

    const userMessage: ChatMessage = {
      id: makeMessageId("user"),
      role: "user",
      content: trimmedQuery,
      createdAt: new Date().toISOString(),
    };
    const previousMessages = messages;
    setMessages([...previousMessages, userMessage]);

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
      const assistantMessage: ChatMessage = {
        id: makeMessageId("assistant"),
        role: "assistant",
        content: payload.answer,
        createdAt: new Date().toISOString(),
        sources: payload.sources,
        experimentId: payload.experiment_id ?? null,
        configHash: payload.config_hash ?? null,
        chunkStrategyId: payload.chunk_strategy_id ?? null,
        generationMetadata: payload.generation_metadata ?? {},
        citationMetadata: payload.citation_metadata ?? {},
      };

      const nextMessages = [...previousMessages, userMessage, assistantMessage];
      setMessages(nextMessages);
      await persistMessages(nextMessages);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Không thể gửi câu hỏi lúc này.";
      setError(message);
      setLastFailedQuery(trimmedQuery);
      setQuery(trimmedQuery);
      setMessages(previousMessages);
    } finally {
      setLoading(false);
    }
  }

  async function persistMessages(nextMessages: ChatMessage[]) {
    if (!sessionId) {
      throw new Error("Chưa sẵn sàng lưu lịch sử chat. Vui lòng thử lại.");
    }

    const { error: updateError } = await supabase
      .from("chat_sessions")
      .update({ messages: nextMessages })
      .eq("id", sessionId);

    if (updateError) {
      throw new Error(`Không thể lưu lịch sử chat: ${updateError.message}`);
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
          <span className="badge-pill">W5-FE-02/03</span>
        </div>

        <p className="chat-helper">{helperText}</p>

        <div className="chat-history-status" role="status">
          {historyLoading
            ? "Đang tải lịch sử chat..."
            : messages.length > 0
              ? `Đã tải ${messages.length} tin nhắn từ lịch sử.`
              : "Chưa có lịch sử chat cho lá số này."}
        </div>

        <div className="chat-message-list" aria-live="polite">
          {!historyLoading && messages.length === 0 && (
            <div className="chat-empty-state">
              <p>Gợi ý: “Cung Mệnh của lá số này nói gì?” hoặc “Các nguồn nào giải thích Thiên Di?”</p>
            </div>
          )}

          {messages.map((message) => (
            <article className={`chat-message ${message.role}`} key={message.id}>
              <div className="chat-message-label">{message.role === "user" ? "Bạn" : "Trợ lý Tử Vi"}</div>
              {message.role === "assistant" ? (
                <AssistantMessage
                  message={message}
                  selectedSourceKey={selectedSourceByMessage[message.id] ?? null}
                  onSelectSource={(sourceKey) =>
                    setSelectedSourceByMessage((current) => ({ ...current, [message.id]: sourceKey }))
                  }
                />
              ) : (
                <p>{message.content}</p>
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

        {error && (
          <div className="chat-error-block">
            <p className="error-message">{error}</p>
            {lastFailedQuery && (
              <button
                className="chat-retry-button"
                disabled={loading || historyLoading}
                onClick={() => submitQuestion(lastFailedQuery)}
                type="button"
              >
                Thử lại câu hỏi vừa lỗi
              </button>
            )}
          </div>
        )}

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="chart-chat-query">
            Câu hỏi về lá số
          </label>
          <textarea
            id="chart-chat-query"
            onChange={(event) => setQuery(event.target.value)}
            placeholder={historyLoading ? "Đang tải lịch sử chat..." : "Nhập câu hỏi về lá số hiện tại..."}
            rows={3}
            value={query}
            disabled={loading || historyLoading}
          />
          <button type="submit" disabled={loading || historyLoading || !query.trim()}>
            {loading ? "Đang hỏi..." : historyLoading ? "Đang tải..." : "Gửi câu hỏi"}
          </button>
        </form>
      </div>
    </section>
  );
}

function AssistantMessage({
  message,
  selectedSourceKey,
  onSelectSource,
}: {
  message: ChatMessage;
  selectedSourceKey: string | null;
  onSelectSource: (sourceKey: string) => void;
}) {
  const sources = message.sources ?? [];

  return (
    <div className="assistant-message-content">
      <div className="assistant-answer">{renderAnswerWithCitations(message.content, sources, onSelectSource)}</div>

      <AssistantFallbackNotice message={message} />

      {sources.length > 0 && (
        <div className="citation-quick-list" aria-label="Mở nguồn trích dẫn">
          <span>Nguồn:</span>
          {sources.map((source, index) => {
            const sourceKey = getSourceKey(source, index);
            return (
              <button key={sourceKey} onClick={() => onSelectSource(sourceKey)} type="button">
                {getSourceMarker(source, index)}
              </button>
            );
          })}
        </div>
      )}

      <SourceCitationPanel
        sources={sources}
        selectedSourceKey={selectedSourceKey}
        onSelectSource={onSelectSource}
      />

      <AssistantRunMeta message={message} />
    </div>
  );
}

function AssistantFallbackNotice({ message }: { message: ChatMessage }) {
  const fallbackReason = readStringFromRecord(message.generationMetadata, "fallback_reason");
  const citationFallback = readBooleanFromRecord(message.citationMetadata, "citation_fallback");

  if (fallbackReason !== "no_context" && !citationFallback) {
    return null;
  }

  return (
    <div className="chat-response-hints">
      {fallbackReason === "no_context" && (
        <p className="notice-message">
          Nguồn hiện có chưa đủ để kết luận chắc chắn. Bạn có thể hỏi cụ thể hơn về một sao, cung hoặc tổ hợp trong lá số.
        </p>
      )}
      {citationFallback && (
        <p className="chat-response-note">
          Hệ thống đang hiển thị nguồn fallback gần nhất vì câu trả lời không nêu marker citation rõ ràng.
        </p>
      )}
    </div>
  );
}

function AssistantRunMeta({ message }: { message: ChatMessage }) {
  if (!message.experimentId && !message.configHash && !message.chunkStrategyId) {
    return null;
  }

  return (
    <div className="chat-run-meta">
      {message.experimentId && <span>Experiment: {message.experimentId}</span>}
      {message.configHash && <span>Config: {message.configHash}</span>}
      {message.chunkStrategyId && <span>Chunk: {message.chunkStrategyId}</span>}
    </div>
  );
}

function renderAnswerWithCitations(
  answer: string,
  sources: ChatSource[],
  onSelectSource: (sourceKey: string) => void,
) {
  if (sources.length === 0) {
    return <p>{answer}</p>;
  }

  const markerToSource = new Map<string, { key: string; label: string }>();
  sources.forEach((source, index) => {
    const marker = source.citation_marker?.trim();
    if (marker) {
      const key = getSourceKey(source, index);
      markerToSource.set(marker, { key, label: `[${marker}]` });
      markerToSource.set(`[${marker}]`, { key, label: `[${marker}]` });
    }
  });

  if (markerToSource.size === 0) {
    return <p>{answer}</p>;
  }

  const markerPattern = Array.from(markerToSource.keys())
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp)
    .join("|");

  const parts = answer.split(new RegExp(`(${markerPattern})`, "g"));
  const renderedParts: ReactNode[] = parts.map((part, index) => {
    const source = markerToSource.get(part);
    if (!source) {
      return part;
    }
    return (
      <button
        className="citation-marker-button"
        key={`${part}-${index}`}
        onClick={() => onSelectSource(source.key)}
        type="button"
      >
        {source.label}
      </button>
    );
  });

  return <p>{renderedParts}</p>;
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
    sources: normalizeSources(body.sources),
    experiment_id: typeof body.experiment_id === "string" ? body.experiment_id : null,
    config_hash: typeof body.config_hash === "string" ? body.config_hash : null,
    chunk_strategy_id: typeof body.chunk_strategy_id === "string" ? body.chunk_strategy_id : null,
    generation_metadata: isRecord(body.generation_metadata) ? body.generation_metadata : {},
    citation_metadata: isRecord(body.citation_metadata) ? body.citation_metadata : {},
  };
}

function normalizeMessages(value: unknown): ChatMessage[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.flatMap((item, index) => {
    if (!isRecord(item) || (item.role !== "user" && item.role !== "assistant") || typeof item.content !== "string") {
      return [];
    }

    return [{
      id: typeof item.id === "string" ? item.id : makeMessageId(`${item.role}-${index}`),
      role: item.role,
      content: item.content,
      createdAt: typeof item.createdAt === "string" ? item.createdAt : new Date().toISOString(),
      sources: normalizeSources(item.sources),
      experimentId: typeof item.experimentId === "string" ? item.experimentId : null,
      configHash: typeof item.configHash === "string" ? item.configHash : null,
      chunkStrategyId: typeof item.chunkStrategyId === "string" ? item.chunkStrategyId : null,
      generationMetadata: isRecord(item.generationMetadata) ? item.generationMetadata : {},
      citationMetadata: isRecord(item.citationMetadata) ? item.citationMetadata : {},
    }];
  });
}

function normalizeSources(value: unknown): ChatSource[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter(isRecord).map((source) => ({
    citation_marker: typeof source.citation_marker === "string" ? source.citation_marker : undefined,
    chunk_id: typeof source.chunk_id === "string" ? source.chunk_id : undefined,
    chunk_hash: typeof source.chunk_hash === "string" ? source.chunk_hash : undefined,
    source_id: typeof source.source_id === "string" ? source.source_id : undefined,
    source_name: typeof source.source_name === "string" ? source.source_name : undefined,
    source_page:
      typeof source.source_page === "number" || typeof source.source_page === "string" ? source.source_page : null,
    excerpt: typeof source.excerpt === "string" ? source.excerpt : undefined,
    score: typeof source.score === "number" ? source.score : null,
    confidence: typeof source.confidence === "number" ? source.confidence : null,
    retrieval_paths: Array.isArray(source.retrieval_paths)
      ? source.retrieval_paths.filter((path): path is string => typeof path === "string")
      : undefined,
  }));
}

function extractErrorMessage(body: unknown): string | null {
  if (!isRecord(body)) {
    return null;
  }
  if (typeof body.error === "string") return body.error;
  if (typeof body.detail === "string") return body.detail;
  return null;
}

function readStringFromRecord(value: unknown, key: string) {
  if (!isRecord(value)) {
    return null;
  }
  return typeof value[key] === "string" ? value[key] : null;
}

function readBooleanFromRecord(value: unknown, key: string) {
  if (!isRecord(value)) {
    return false;
  }
  return value[key] === true;
}

function makeMessageId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}