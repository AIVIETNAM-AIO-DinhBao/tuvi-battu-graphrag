"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { BatuBoard, type BatuChartData } from "../../../components/BatuBoard";
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
  const [sessionEmail, setSessionEmail] = useState<string | null>(null);
  const [chart, setChart] = useState<ChartRow | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadChart() {
      const { data: sessionData } = await supabase.auth.getSession();
      if (!sessionData.session) {
        router.push("/login");
        return;
      }

      if (!chartId) {
        setError("Chart id không hợp lệ.");
        setLoading(false);
        return;
      }

      setSessionEmail(sessionData.session.user.email || null);

      const { data, error: fetchError } = await supabase
        .from("la_so")
        .select(
          "id,label,birth_date,birth_time,gender,chart_system,chart_version,chart_data,created_at",
        )
        .eq("id", chartId)
        .single();

      if (cancelled) {
        return;
      }

      if (fetchError) {
        setError(`Không thể tải chart: ${fetchError.message}`);
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
    return <main className="loading-state">Đang tải chart...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Chi tiết chart</h1>
          <p>Người dùng: {sessionEmail}</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => router.push("/dashboard")}>
          Về dashboard
        </button>
      </header>

      {error && <p className="error-message">{error}</p>}

      {chart && (
        <section className="panel">
          <h2>{chart.label}</h2>
          <dl className="detail-list">
            <div>
              <dt>Chart ID</dt>
              <dd>{chart.id}</dd>
            </div>
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
              <dt>Loại chart</dt>
              <dd>{formatChartSystem(chart.chart_system)}</dd>
            </div>
            <div>
              <dt>Phiên bản chart</dt>
              <dd>{chart.chart_version ?? "N/A"}</dd>
            </div>
          </dl>

          <ChartVisualizer chartSystem={chart.chart_system} chartData={chart.chart_data} />

          <details className="debug-details">
            <summary>Dữ liệu debug của chart</summary>
            <pre className="json-preview">{JSON.stringify(chart.chart_data, null, 2)}</pre>
          </details>
        </section>
      )}
    </main>
  );
}

function ChartVisualizer({
  chartSystem,
  chartData,
}: {
  chartSystem: string;
  chartData: unknown;
}) {
  if (chartSystem === "TUVI") {
    if (isTuViChartData(chartData)) {
      return <TuViBoard chart={chartData} />;
    }

    return <VisualizerError message="Dữ liệu Tử Vi không đúng định dạng." />;
  }

  if (chartSystem === "BATU") {
    if (isBatuChartData(chartData)) {
      return <BatuBoard chart={chartData} />;
    }

    return <VisualizerError message="Dữ liệu Bát Tự không đúng định dạng." />;
  }

  if (chartSystem === "TUVI_BATU") {
    if (!isRecord(chartData)) {
      return <VisualizerError message="Dữ liệu chart kết hợp không đúng định dạng." />;
    }

    const tuvi = chartData.tuvi;
    const batu = chartData.batu;

    return (
      <div className="combined-boards">
        {isTuViChartData(tuvi) ? (
          <TuViBoard chart={tuvi} />
        ) : (
          <VisualizerError message="Dữ liệu Tử Vi trong chart kết hợp không đúng định dạng." />
        )}
        {isBatuChartData(batu) ? (
          <BatuBoard chart={batu} />
        ) : (
          <VisualizerError message="Dữ liệu Bát Tự trong chart kết hợp không đúng định dạng." />
        )}
      </div>
    );
  }

  return <VisualizerError message={`Chart system chưa được hỗ trợ: ${chartSystem}`} />;
}

function VisualizerError({ message }: { message: string }) {
  return (
    <section className="visualizer-section">
      <div className="board-message">
        <h3>Không thể hiển thị visualizer</h3>
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
  if (value === "BATU") return "Bát Tự";
  if (value === "TUVI_BATU") return "Tử Vi + Bát Tự";
  return value || "N/A";
}

function isTuViChartData(value: unknown): value is TuViChartData {
  return isRecord(value) && value.chart_type === "TUVI" && isRecord(value.palaces);
}

function isBatuChartData(value: unknown): value is BatuChartData {
  return isRecord(value) && value.chart_type === "BATU" && isRecord(value.pillars);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
