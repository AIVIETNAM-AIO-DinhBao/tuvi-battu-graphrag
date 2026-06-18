"use client";

import type { ReactNode } from "react";

export interface BatuPillar {
  thien_can?: string;
  dia_chi?: string;
  nap_am?: string;
  hidden_stems?: string[];
}

export interface BatuChartData {
  chart_type?: string;
  version?: string;
  metadata?: {
    label?: string;
    birth_date?: string;
    birth_time?: string;
    gender?: string;
  };
  pillars?: {
    year?: BatuPillar;
    month?: BatuPillar;
    day?: BatuPillar;
    hour?: BatuPillar;
  };
  elements?: {
    elements_count?: Record<string, number>;
  };
}

interface BatuBoardProps {
  chart: BatuChartData;
}

const PILLARS = [
  ["year", "Năm"],
  ["month", "Tháng"],
  ["day", "Ngày"],
  ["hour", "Giờ"],
] as const;

const ELEMENT_LABELS: Record<string, string> = {
  WOOD: "Mộc",
  FIRE: "Hỏa",
  EARTH: "Thổ",
  METAL: "Kim",
  WATER: "Thủy",
};

export function BatuBoard({ chart }: BatuBoardProps) {
  const pillars = chart.pillars ?? {};
  const hasAnyPillar = PILLARS.some(([key]) => Boolean(pillars[key]));

  if (!hasAnyPillar) {
    return (
      <BoardMessage title="Không thể hiển thị bảng Bát Tự">
        Dữ liệu chart hiện có không có thông tin bốn trụ.
      </BoardMessage>
    );
  }

  const elementEntries = Object.entries(chart.elements?.elements_count ?? {});
  const maxElementValue = Math.max(...elementEntries.map(([, value]) => value), 1);

  return (
    <section className="visualizer-section" aria-labelledby="batu-board-title">
      <div className="visualizer-heading">
        <div>
          <p className="eyebrow">Bát Tự</p>
          <h3 id="batu-board-title">Bảng bốn trụ</h3>
        </div>
        <p>
          {chart.metadata?.birth_date ?? "N/A"} - {chart.metadata?.birth_time ?? "N/A"}
        </p>
      </div>

      <div className="batu-grid">
        {PILLARS.map(([key, label]) => {
          const pillar = pillars[key];
          const hiddenStems = pillar?.hidden_stems ?? [];

          return (
            <article className="batu-pillar" key={key}>
              <h4>{label}</h4>
              <div className="batu-stem-branch">
                <span>{pillar?.thien_can || "N/A"}</span>
                <span>{pillar?.dia_chi || "N/A"}</span>
              </div>
              <dl>
                <div>
                  <dt>Nạp âm</dt>
                  <dd>{pillar?.nap_am || "N/A"}</dd>
                </div>
                <div>
                  <dt>Ẩn can</dt>
                  <dd>{hiddenStems.length > 0 ? hiddenStems.join(", ") : "N/A"}</dd>
                </div>
              </dl>
            </article>
          );
        })}
      </div>

      {elementEntries.length > 0 && (
        <div className="batu-elements" aria-label="Ngũ hành">
          {elementEntries.map(([element, value]) => (
            <div className="element-row" key={element}>
              <span>{ELEMENT_LABELS[element] ?? element}</span>
              <div className="element-meter" aria-hidden="true">
                <div style={{ width: `${Math.max((value / maxElementValue) * 100, 4)}%` }} />
              </div>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function BoardMessage({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="visualizer-section">
      <div className="board-message">
        <h3>{title}</h3>
        <p>{children}</p>
      </div>
    </section>
  );
}
