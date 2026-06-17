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
  TUVI: "Tu Vi",
  BATU: "Bat Tu",
  TUVI_BATU: "Tu Vi + Bat Tu",
};

export function ChartSummaryCard({ chart, onOpen }: ChartSummaryCardProps) {
  return (
    <button
      type="button"
      className="chart-summary-card"
      onClick={() => onOpen(chart.id)}
      aria-label={`Mo chart ${chart.label}`}
    >
      <span className="chart-type-chip">{CHART_SYSTEM_LABELS[chart.chart_system]}</span>
      <strong>{chart.label}</strong>
      <dl>
        <div>
          <dt>Birth</dt>
          <dd>
            {formatDate(chart.birth_date)} - {chart.birth_time}
          </dd>
        </div>
        <div>
          <dt>Gender</dt>
          <dd>{formatGender(chart.gender)}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{formatDate(chart.created_at)}</dd>
        </div>
      </dl>
    </button>
  );
}

function formatGender(value: string) {
  if (value === "male") return "Nam";
  if (value === "female") return "Nu";
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
