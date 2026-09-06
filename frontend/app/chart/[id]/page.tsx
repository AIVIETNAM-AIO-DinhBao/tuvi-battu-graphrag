"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ChatInterface } from "../../../components/ChatInterface";
import { TuViBoard, type TuViChartData } from "../../../components/TuViBoard";
import { supabase } from "../../../lib/supabaseClient";

interface ChartRow {
  id: string;
  label: string;
  birth_date: string;
  birth_time: string;
  gender: string;
  chart_system: string;
  chart_version: string | null;
  chart_data: unknown;
  created_at: string;
}

export default function ChartDetailPage() {
  const params = useParams();
  const rawChartId = params?.id;
  const chartId = Array.isArray(rawChartId) ? rawChartId[0] : rawChartId ?? "";
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [chart, setChart] = useState<ChartRow | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chartMissing, setChartMissing] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadChart() {
      setError(null);
      setChartMissing(false);

      const { data: sessionData } = await supabase.auth.getSession();
      if (!sessionData.session) {
        router.replace("/login");
        return;
      }

      if (!chartId) {
      setError("Không tìm thấy lá số cần mở.");
        setLoading(false);
        return;
      }

      const userId = sessionData.session.user.id;

      const { data, error: fetchError } = await supabase
        .from("la_so")
        .select(
          "id,label,birth_date,birth_time,gender,chart_system,chart_data,created_at",
        )
        .eq("id", chartId)
        .eq("user_id", userId)
        .maybeSingle();

      if (cancelled) {
        return;
      }

      if (fetchError) {
        setError("Không thể tải lá số lúc này. Vui lòng thử lại.");
      } else if (!data) {
        setChartMissing(true);
        setError("Lá số không tồn tại hoặc bạn không có quyền xem. Hãy quay lại trang chủ để chọn một lá số khác.");
      } else {
        setChart(data as ChartRow);
      }

      setLoading(false);
    }

    loadChart();

    return () => {
      cancelled = true;
    };
  }, [chartId, router]);

  if (loading) {
    return <main className="loading-state">Đang tải lá số...</main>;
  }

  return (
    <main className="chart-detail-main">
      <header className="page-header chart-detail-page-header">
        <h1>Chi tiết lá số</h1>
        <button type="button" className="secondary-button" onClick={() => router.push("/dashboard")}>
          Về trang chủ
        </button>
      </header>

      {error && !chart && (
        <section className="panel chart-error-panel">
          <h2>Không thể mở lá số</h2>
          <p className="error-message">{error}</p>
          <div className="header-actions">
            <button type="button" className="secondary-button" onClick={() => router.push("/dashboard")}>
              Quay lại trang chủ
            </button>
          </div>
        </section>
      )}

      {chartMissing && !chart && null}

      {chart && (
        <div className="chart-workspace">
        <section className="panel chart-detail-panel">
          <div className="section-heading-row">
            <h2>{chart.label}</h2>
            <span className="badge-pill">{formatChartSystem(chart.chart_system)}</span>
          </div>

          <dl className="detail-list">
            <div>
              <dt>Ngày sinh</dt>
              <dd>{chart.birth_date}</dd>
            </div>
            <div>
              <dt>Giờ sinh</dt>
              <dd>{chart.birth_time}</dd>
            </div>
            <div>
              <dt>Giới tính</dt>
              <dd>{formatGender(chart.gender)}</dd>
            </div>
            <div>
              <dt>Ngày tạo</dt>
              <dd>{formatDateTime(chart.created_at)}</dd>
            </div>
          </dl>

          {error && <p className="error-message">{error}</p>}

          <ChartVisualizer chartData={chart.chart_data} />

        </section>
        <ChatInterface chartId={chart.id} chartLabel={chart.label} chartData={chart.chart_data} />
        </div>
      )}
    </main>
  );
}

function ChartVisualizer({
  chartData,
}: {
  chartData: unknown;
}) {
  if (isTuViChartData(chartData)) {
    return <TuViBoard chart={chartData} />;
  }

  return <VisualizerError message="Dữ liệu Tử Vi không đúng định dạng." />;
}

function VisualizerError({ message }: { message: string }) {
  return (
    <section className="visualizer-section">
      <div className="board-message">
        <h3>Không thể hiển thị sơ đồ lá số</h3>
        <p>{message}</p>
      </div>
    </section>
  );
}

function formatGender(value: string) {
  if (value === "male") return "Nam";
  if (value === "female") return "Nữ";
  return value || "N/A";
}

function formatChartSystem(value: string) {
  if (value === "TUVI") return "Tử Vi";
  return value || "N/A";
}

function formatDateTime(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value || "N/A";
  }
  return parsed.toLocaleString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function isTuViChartData(value: unknown): value is TuViChartData {
  return isRecord(value) && value.chart_type === "TUVI" && isRecord(value.palaces);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
