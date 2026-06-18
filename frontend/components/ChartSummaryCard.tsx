"use client";

export type ChartSystem = "TUVI" | "BATU" | "TUVI_BATU";

export interface ChartSummary {
  id: string;
  label: string;
  birth_date: string;
  birth_time: string;
  gender: string;
  chart_system: ChartSystem;
  created_at: string;
}

interface ChartSummaryCardProps {
  chart: ChartSummary;
  onOpen: (id: string) => void;
}

const CHART_SYSTEM_LABELS: Record<ChartSystem, string> = {
  TUVI: "Tử Vi",
  BATU: "Bát Tự",
  TUVI_BATU: "Tử Vi + Bát Tự",
};

export function ChartSummaryCard({ chart, onOpen }: ChartSummaryCardProps) {
  return (
    <button
      type="button"
      className="chart-summary-card"
      onClick={() => onOpen(chart.id)}
      aria-label={`Mở chart ${chart.label}`}
    >
      <span className="chart-type-chip">{CHART_SYSTEM_LABELS[chart.chart_system]}</span>
      <strong>{chart.label}</strong>
      <dl>
        <div>
          <dt>Ngày sinh</dt>
          <dd>
            {formatDate(chart.birth_date)} - {chart.birth_time}
          </dd>
        </div>
        <div>
          <dt>Giới tính</dt>
          <dd>{formatGender(chart.gender)}</dd>
        </div>
        <div>
          <dt>Ngày tạo</dt>
          <dd>{formatDate(chart.created_at)}</dd>
        </div>
      </dl>
    </button>
  );
}

function formatGender(value: string) {
  if (value === "male") return "Nam";
  if (value === "female") return "Nữ";
  return value || "N/A";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value || "N/A";
  }

  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}
