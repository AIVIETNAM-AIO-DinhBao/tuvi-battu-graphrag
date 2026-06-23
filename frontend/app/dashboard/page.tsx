"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChartSummaryCard, type ChartSummary } from "../../components/ChartSummaryCard";
import { supabase } from "../../lib/supabaseClient";

type Gender = "male" | "female";

interface CreateChartFormState {
  label: string;
  birth_date: string;
  birth_time: string;
  gender: Gender;
  nam_xem_han: string;
}

interface SessionUser {
  id: string;
  email?: string;
}

const CHART_VERSION = "tuvi-v1";
const CURRENT_YEAR = new Date().getFullYear();

const initialFormState: CreateChartFormState = {
  label: "",
  birth_date: "",
  birth_time: "08:00",
  gender: "male",
  nam_xem_han: String(CURRENT_YEAR),
};

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [user, setUser] = useState<SessionUser | null>(null);
  const [charts, setCharts] = useState<ChartSummary[]>([]);
  const [chartsLoading, setChartsLoading] = useState(false);
  const [chartsError, setChartsError] = useState<string | null>(null);
  const [form, setForm] = useState<CreateChartFormState>(initialFormState);
  const [error, setError] = useState<string | null>(null);

  const userEmail = user?.email ?? null;

  useEffect(() => {
    let cancelled = false;

    async function loadCharts(userId: string) {
      setChartsLoading(true);
      setChartsError(null);

      const { data, error } = await supabase
        .from("la_so")
        .select("id,label,birth_date,birth_time,gender,chart_system,created_at")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (cancelled) {
        return;
      }

      if (error) {
        setChartsError(`Không thể tải danh sách chart: ${error.message}`);
        setCharts([]);
      } else {
        setCharts((data ?? []) as ChartSummary[]);
      }

      setChartsLoading(false);
    }

    async function loadDashboard() {
      const { data } = await supabase.auth.getSession();
      if (!data.session) {
        router.push("/login");
        return;
      }

      const sessionUser = {
        id: data.session.user.id,
        email: data.session.user.email ?? undefined,
      };

      if (cancelled) {
        return;
      }

      setUser(sessionUser);
      setLoading(false);

      await loadCharts(sessionUser.id);
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  const updateField = <K extends keyof CreateChartFormState>(
    field: K,
    value: CreateChartFormState[K],
  ) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const scrollToCreateChart = () => {
    document.getElementById("create-chart")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const openChart = (chartId: string) => {
    router.push(`/chart/${chartId}`);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!user) {
      router.push("/login");
      return;
    }

    const validationError = validateForm(form);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitLoading(true);

    try {
      const normalizedForm = {
        ...form,
        label: form.label.trim(),
      };

      const chartData = await calculateChartData(normalizedForm);

      const { error: profileError } = await supabase.from("profiles").upsert({
        id: user.id,
        display_name: user.email ?? null,
      });

      if (profileError) {
        throw new Error(`Không thể tạo profile: ${profileError.message}`);
      }

      const { data: newRow, error: insertError } = await supabase
        .from("la_so")
        .insert({
          user_id: user.id,
          label: normalizedForm.label,
          birth_date: normalizedForm.birth_date,
          birth_time: normalizedForm.birth_time,
          gender: normalizedForm.gender,
          chart_system: "TUVI",
          chart_data: chartData,
          chart_version: CHART_VERSION,
        })
        .select("id")
        .single();

      if (insertError) {
        throw new Error(`Không thể lưu chart: ${insertError.message}`);
      }

      if (!newRow?.id) {
        throw new Error("Supabase không trả về id chart mới.");
      }

      router.push(`/chart/${newRow.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tạo chart thất bại.");
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <main className="loading-state">Đang tải dữ liệu người dùng...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Xin chào, {userEmail ?? "người dùng"}.</p>
        </div>
        <div className="header-actions">
          <button type="button" className="secondary-button" onClick={scrollToCreateChart}>
            Tạo chart mới
          </button>
          <button type="button" className="secondary-button" onClick={handleLogout}>
            Đăng xuất
          </button>
        </div>
      </header>

      <section className="panel" id="create-chart">
        <h2>Tạo chart mới</h2>
        <form className="chart-form" onSubmit={handleSubmit}>
          <label>
            Tên chart
            <input
              type="text"
              value={form.label}
              onChange={(event) => updateField("label", event.target.value)}
              placeholder="Lá số của tôi"
              disabled={submitLoading}
              required
            />
          </label>

          <div className="form-grid">
            <label>
              Ngày sinh
              <input
                type="date"
                value={form.birth_date}
                onChange={(event) => updateField("birth_date", event.target.value)}
                disabled={submitLoading}
                required
              />
            </label>

            <label>
              Giờ sinh
              <input
                type="time"
                value={form.birth_time}
                onChange={(event) => updateField("birth_time", event.target.value)}
                disabled={submitLoading}
                required
              />
            </label>
          </div>

          <div className="form-grid">
            <label>
              Giới tính
              <select
                value={form.gender}
                onChange={(event) => updateField("gender", event.target.value as Gender)}
                disabled={submitLoading}
              >
                <option value="male">Nam</option>
                <option value="female">Nữ</option>
              </select>
            </label>

            <label>
              Năm xem hạn
              <input
                type="number"
                min="1900"
                max="2100"
                value={form.nam_xem_han}
                onChange={(event) => updateField("nam_xem_han", event.target.value)}
                disabled={submitLoading}
                required
              />
            </label>
          </div>

          <button type="submit" disabled={submitLoading}>
            {submitLoading ? "Đang tính và lưu chart..." : "Tạo chart"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
      </section>

      <section className="panel">
        <div className="section-heading-row">
          <div>
            <h2>Charts đã lưu</h2>
            <p>
              {charts.length > 0
                ? `${charts.length} chart đã lưu.`
                : "Danh sách chart của bạn."}
            </p>
          </div>
          <button type="button" className="secondary-button" onClick={scrollToCreateChart}>
            Tạo chart mới
          </button>
        </div>

        {chartsLoading && <p className="form-note">Đang tải danh sách chart...</p>}
        {chartsError && <p className="error-message">{chartsError}</p>}

        {!chartsLoading && !chartsError && charts.length === 0 && (
          <div className="empty-state">
            <h3>Chưa có chart nào</h3>
            <p>Tạo chart đầu tiên để xem bảng Tử Vi tại trang chi tiết.</p>
            <button type="button" onClick={scrollToCreateChart}>
              Tạo chart mới
            </button>
          </div>
        )}

        {!chartsLoading && !chartsError && charts.length > 0 && (
          <div className="chart-list-grid">
            {charts.map((chart) => (
              <ChartSummaryCard chart={chart} key={chart.id} onOpen={openChart} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function validateForm(form: CreateChartFormState): string | null {
  if (!form.label.trim()) {
    return "Tên chart không được để trống.";
  }

  const dateParts = parseBirthDate(form.birth_date);
  if (!dateParts) {
    return "Ngày sinh phải là ngày Gregorian hợp lệ.";
  }

  if (!/^\d{2}:\d{2}$/.test(form.birth_time)) {
    return "Giờ sinh phải có định dạng HH:MM.";
  }

  const [hour, minute] = form.birth_time.split(":").map(Number);
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
    return "Giờ sinh phải nằm trong khoảng 00:00-23:59.";
  }

  const namXemHan = Number(form.nam_xem_han);
  if (!Number.isInteger(namXemHan) || namXemHan < 1900 || namXemHan > 2100) {
    return "Năm xem hạn phải nằm trong khoảng 1900-2100.";
  }

  return null;
}

async function calculateChartData(form: CreateChartFormState) {
  return calculateTuVi(form);
}

async function calculateTuVi(form: CreateChartFormState) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!apiBaseUrl) {
    throw new Error("Thiếu cấu hình NEXT_PUBLIC_API_BASE_URL cho Tử Vi engine.");
  }

  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/chart/tuvi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      label: form.label,
      birth_date: form.birth_date,
      birth_time: form.birth_time,
      gender: form.gender,
      nam_xem_han: Number(form.nam_xem_han),
    }),
  });

  return parseEngineResponse(response, "Tử Vi");
}

async function parseEngineResponse(response: Response, engineName: string) {
  let body: unknown = null;

  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const message = extractErrorMessage(body);
    throw new Error(`${engineName} engine lỗi: ${message || response.statusText}`);
  }

  return body;
}

function extractErrorMessage(body: unknown): string | null {
  if (!body || typeof body !== "object") {
    return null;
  }

  const record = body as Record<string, unknown>;
  const detail = record.detail;
  const error = record.error;

  if (typeof detail === "string") return detail;
  if (typeof error === "string") return error;
  return null;
}

function parseBirthDate(value: string) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const date = new Date(Date.UTC(year, month - 1, day));

  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    return null;
  }

  return { year, month, day };
}
