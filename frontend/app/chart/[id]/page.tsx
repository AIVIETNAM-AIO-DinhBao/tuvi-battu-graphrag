"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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

          <h3>Stored chart data</h3>
          <pre className="json-preview">{JSON.stringify(chart.chart_data, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
