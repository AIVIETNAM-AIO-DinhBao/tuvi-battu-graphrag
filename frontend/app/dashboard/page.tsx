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
        setChartsError("Không thể tải danh sách lá số lúc này. Vui lòng thử lại.");
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

      const hasDuplicateLabel = charts.some(
        (chart) => chart.label.trim().localeCompare(normalizedForm.label, "vi", { sensitivity: "accent" }) === 0,
      );
      if (hasDuplicateLabel) {
        throw new Error("Bạn đã có lá số với họ tên này. Hãy dùng tên khác để dễ tìm lại.");
      }

      const chartData = await calculateChartData(normalizedForm);

      const { error: profileError } = await supabase.from("profiles").upsert({
        id: user.id,
        display_name: user.email ?? null,
      });

      if (profileError) {
        throw new Error("Không thể lưu thông tin tài khoản lúc này. Vui lòng thử lại.");
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
        if (insertError.code === "23505") {
          throw new Error("Bạn đã có lá số với họ tên này. Hãy dùng tên khác để dễ tìm lại.");
        }
        throw new Error("Không thể lưu lá số lúc này. Vui lòng thử lại.");
      }

      if (!newRow?.id) {
        throw new Error("Không thể tạo lá số mới. Vui lòng thử lại.");
      }

      router.push(`/chart/${newRow.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tạo lá số thất bại.");
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <main className="loading-state">Đang tải thông tin của bạn...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Lá số của bạn</h1>
          <p>Xin chào, {userEmail ?? "người dùng"}.</p>
        </div>
        <div className="header-actions">
          <button type="button" className="secondary-button" onClick={() => router.push("/profile")}>
            Hồ sơ
          </button>
          <button type="button" className="secondary-button" onClick={scrollToCreateChart}>
            Tạo lá số
          </button>
          <button type="button" className="secondary-button" onClick={handleLogout}>
            Đăng xuất
          </button>
        </div>
      </header>

      <section className="panel" id="create-chart">
        <h2>Tạo lá số Tử Vi</h2>
        <form className="chart-form" onSubmit={handleSubmit}>
          <label>
            Họ tên
            <input
              type="text"
              value={form.label}
              onChange={(event) => updateField("label", event.target.value)}
              placeholder="Ví dụ: Nguyễn Văn A"
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
            {submitLoading ? "Đang lập và lưu lá số..." : "Tạo lá số"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
      </section>

      <section className="panel">
        <div className="section-heading-row">
          <div>
            <h2>Lá số đã lưu</h2>
            <p>
              {charts.length > 0
                ? `${charts.length} lá số đã lưu.`
                : "Danh sách lá số của bạn."}
            </p>
          </div>
          <button type="button" className="secondary-button" onClick={scrollToCreateChart}>
            Tạo lá số
          </button>
        </div>

        {chartsLoading && <p className="form-note">Đang tải danh sách lá số...</p>}
        {chartsError && <p className="error-message">{chartsError}</p>}

        {!chartsLoading && !chartsError && charts.length === 0 && (
          <div className="empty-state">
            <h3>Bạn chưa có lá số nào</h3>
            <p>Tạo lá số đầu tiên để xem sơ đồ 12 cung và nhận luận giải.</p>
            <button type="button" onClick={scrollToCreateChart}>
              Tạo lá số
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
    return "Họ tên không được để trống.";
  }

  const dateParts = parseBirthDate(form.birth_date);
  if (!dateParts) {
    return "Ngày sinh chưa hợp lệ.";
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
    throw new Error("Chức năng lập lá số hiện chưa sẵn sàng. Vui lòng thử lại sau.");
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

  return parseEngineResponse(response, "Lập lá số");
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
    throw new Error(`${engineName} không thành công: ${message || response.statusText}`);
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
