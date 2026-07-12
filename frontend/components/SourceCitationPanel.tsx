"use client";

import { ChatSource } from "../lib/chatTypes";

interface SourceCitationPanelProps {
  sources: ChatSource[];
  selectedSourceKey?: string | null;
  onSelectSource?: (key: string) => void;
}

export function SourceCitationPanel({
  sources,
  selectedSourceKey,
  onSelectSource,
}: SourceCitationPanelProps) {
  if (sources.length === 0) {
    return (
      <section className="source-citation-panel" aria-label="Nguồn trích dẫn">
        <h3>Nguồn trích dẫn</h3>
        <p className="source-citation-empty">Pipeline chưa trả về nguồn cho câu trả lời này.</p>
      </section>
    );
  }

  return (
    <section className="source-citation-panel" aria-label="Nguồn trích dẫn">
      <div className="source-citation-heading">
        <h3>Nguồn trích dẫn</h3>
        <span>{sources.length} nguồn</span>
      </div>

      <div className="source-citation-list">
        {sources.map((source, index) => {
          const sourceKey = getSourceKey(source, index);
          const marker = getSourceMarker(source, index);
          const selected = sourceKey === selectedSourceKey;

          return (
            <article
              className={`source-citation-card${selected ? " is-selected" : ""}`}
              id={`source-${sourceKey}`}
              key={sourceKey}
            >
              <button
                aria-pressed={selected}
                className="source-citation-title"
                onClick={() => onSelectSource?.(sourceKey)}
                type="button"
              >
                <span>{marker}</span>
                <strong>{source.source_name || source.source_id || "Nguồn Tử Vi"}</strong>
              </button>

              <p className="source-citation-excerpt">{source.excerpt || "Không có excerpt."}</p>

              <div className="source-citation-metadata">
                {source.source_page ? <span>Trang {source.source_page}</span> : <span>Trang N/A</span>}
                {typeof source.score === "number" && <span>Score {source.score.toFixed(3)}</span>}
                {typeof source.confidence === "number" && <span>Conf {source.confidence.toFixed(2)}</span>}
                {Array.isArray(source.retrieval_paths) && source.retrieval_paths.length > 0 && (
                  <span>{source.retrieval_paths.join(" + ")}</span>
                )}
              </div>

              <details className="source-provenance-details">
                <summary>Provenance kỹ thuật</summary>
                <dl>
                  <div>
                    <dt>source_id</dt>
                    <dd>{source.source_id || "N/A"}</dd>
                  </div>
                  <div>
                    <dt>chunk_id</dt>
                    <dd>{source.chunk_id || "N/A"}</dd>
                  </div>
                  <div>
                    <dt>chunk_hash</dt>
                    <dd>{source.chunk_hash || "N/A"}</dd>
                  </div>
                </dl>
              </details>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export function getSourceMarker(source: ChatSource, index: number) {
  return source.citation_marker ? `[${source.citation_marker}]` : `[S${index + 1}]`;
}

export function getSourceKey(source: ChatSource, index: number) {
  return (
    source.citation_marker ||
    source.chunk_id ||
    source.chunk_hash ||
    [source.source_id, source.source_page, index].filter(Boolean).join("-") ||
    `source-${index}`
  );
}