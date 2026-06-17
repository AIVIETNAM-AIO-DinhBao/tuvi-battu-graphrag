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
        setError("Chart id khong hop le.");
        setLoading(false);
        return;
      }

      setSessionEmail(sessionData.session.user.email || null);

      const { data, error: fetchError } = await supabase
        .from("la_so")
        .select(
          "id,label,birth_date,birth_time,gender,chart_system,chart_version,chart_data,created_at"
        )
        .eq("id", chartId)
        .single();

      if (cancelled) {
        return;
      }

      if (fetchError) {
        setError(`Khong the tai chart: ${fetchError.message}`);
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
    return <main>Dang tai chart...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Chart Detail</h1>
          <p>Nguoi dung: {sessionEmail}</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => router.push("/dashboard")}>
          Ve dashboard
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
              <dt>Birth date</dt>
              <dd>{chart.birth_date}</dd>
            </div>
            <div>
              <dt>Birth time</dt>
              <dd>{chart.birth_time}</dd>
            </div>
            <div>
              <dt>Gender</dt>
              <dd>{chart.gender}</dd>
            </div>
            <div>
              <dt>Chart system</dt>
              <dd>{chart.chart_system}</dd>
            </div>
            <div>
              <dt>Chart version</dt>
              <dd>{chart.chart_version ?? "N/A"}</dd>
            </div>
          </dl>

          <ChartVisualizer chartSystem={chart.chart_system} chartData={chart.chart_data} />

          <details className="debug-details">
            <summary>Debug chart data</summary>
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

    return <VisualizerError message="Du lieu Tu Vi khong dung dinh dang." />;
  }

  if (chartSystem === "BATU") {
    if (isBatuChartData(chartData)) {
      return <BatuBoard chart={chartData} />;
    }

    return <VisualizerError message="Du lieu Bat Tu khong dung dinh dang." />;
  }

  if (chartSystem === "TUVI_BATU") {
    if (!isRecord(chartData)) {
      return <VisualizerError message="Du lieu chart ket hop khong dung dinh dang." />;
    }

    const tuvi = chartData.tuvi;
    const batu = chartData.batu;

    return (
      <div className="combined-boards">
        {isTuViChartData(tuvi) ? (
          <TuViBoard chart={tuvi} />
        ) : (
          <VisualizerError message="Du lieu Tu Vi trong chart ket hop khong dung dinh dang." />
        )}
        {isBatuChartData(batu) ? (
          <BatuBoard chart={batu} />
        ) : (
          <VisualizerError message="Du lieu Bat Tu trong chart ket hop khong dung dinh dang." />
        )}
      </div>
    );
  }

  return <VisualizerError message={`Chart system chua duoc ho tro: ${chartSystem}`} />;
}

function VisualizerError({ message }: { message: string }) {
  return (
    <section className="visualizer-section">
      <div className="board-message">
        <h3>Khong the hien thi visualizer</h3>
        <p>{message}</p>
      </div>
    </section>
  );
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
