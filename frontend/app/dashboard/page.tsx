"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

type ChartSystem = "TUVI" | "BATU" | "TUVI_BATU";
type Gender = "male" | "female";

interface CreateChartFormState {
  label: string;
  birth_date: string;
  birth_time: string;
  gender: Gender;
  chart_system: ChartSystem;
}

interface SessionUser {
  id: string;
  email?: string;
}

const BATU_SUPPORTED_YEAR_MIN = 1930;
const BATU_SUPPORTED_YEAR_MAX = 2048;
const CHART_VERSION = "1.0";

const initialFormState: CreateChartFormState = {
  label: "",
  birth_date: "",
  birth_time: "08:00",
  gender: "male",
  chart_system: "TUVI",
};

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [user, setUser] = useState<SessionUser | null>(null);
  const [form, setForm] = useState<CreateChartFormState>(initialFormState);
  const [error, setError] = useState<string | null>(null);

  const userEmail = user?.email ?? null;
  const isBatuSystem = useMemo(
    () => form.chart_system === "BATU" || form.chart_system === "TUVI_BATU",
    [form.chart_system]
  );

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (!data.session) {
        router.push("/login");
        return;
      }

      setUser({
        id: data.session.user.id,
        email: data.session.user.email ?? undefined,
      });
      setLoading(false);
    });
  }, [router]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  const updateField = <K extends keyof CreateChartFormState>(
    field: K,
    value: CreateChartFormState[K]
  ) => {
    setForm((current) => ({ ...current, [field]: value }));
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
        throw new Error(`Khong the tao profile: ${profileError.message}`);
      }

      const { data: newRow, error: insertError } = await supabase
        .from("la_so")
        .insert({
          user_id: user.id,
          label: normalizedForm.label,
          birth_date: normalizedForm.birth_date,
          birth_time: normalizedForm.birth_time,
          gender: normalizedForm.gender,
          chart_system: normalizedForm.chart_system,
          chart_data: chartData,
          chart_version: CHART_VERSION,
        })
        .select("id")
        .single();

      if (insertError) {
        throw new Error(`Khong the luu chart: ${insertError.message}`);
      }

      if (!newRow?.id) {
        throw new Error("Supabase khong tra ve id chart moi.");
      }

      router.push(`/chart/${newRow.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tao chart that bai.");
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <main>Dang tai du lieu nguoi dung...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Xin chao, {userEmail ?? "Nguoi dung"}.</p>
        </div>
        <button type="button" className="secondary-button" onClick={handleLogout}>
          Dang xuat
        </button>
      </header>

      <section className="panel">
        <h2>Create new chart</h2>
        <form className="chart-form" onSubmit={handleSubmit}>
          <label>
            Label
            <input
              type="text"
              value={form.label}
              onChange={(event) => updateField("label", event.target.value)}
              placeholder="La so cua toi"
              disabled={submitLoading}
              required
            />
          </label>

          <div className="form-grid">
            <label>
              Birth date
              <input
                type="date"
                value={form.birth_date}
                onChange={(event) => updateField("birth_date", event.target.value)}
                disabled={submitLoading}
                required
              />
            </label>

            <label>
              Birth time
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
              Gender
              <select
                value={form.gender}
                onChange={(event) => updateField("gender", event.target.value as Gender)}
                disabled={submitLoading}
              >
                <option value="male">Nam</option>
                <option value="female">Nu</option>
              </select>
            </label>

            <label>
              Chart type
              <select
                value={form.chart_system}
                onChange={(event) =>
                  updateField("chart_system", event.target.value as ChartSystem)
                }
                disabled={submitLoading}
              >
                <option value="TUVI">Tu Vi</option>
                <option value="BATU">Bat Tu</option>
                <option value="TUVI_BATU">Tu Vi + Bat Tu</option>
              </select>
            </label>
          </div>

          {isBatuSystem && (
            <p className="form-note">
              Bat Tu hien ho tro nam {BATU_SUPPORTED_YEAR_MIN}-{BATU_SUPPORTED_YEAR_MAX}.
            </p>
          )}

          <button type="submit" disabled={submitLoading}>
            {submitLoading ? "Dang tinh va luu chart..." : "Tao chart"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
      </section>

      <section className="panel">
        <h2>Chart sample</h2>
        <p>Trang chart co ban se hien thi metadata chart da luu.</p>
        <a href="/chart/00000000-0000-0000-0000-000000000010">Xem chart vi du</a>
      </section>
    </main>
  );
}

function validateForm(form: CreateChartFormState): string | null {
  if (!form.label.trim()) {
    return "Label khong duoc de trong.";
  }

  const dateParts = parseBirthDate(form.birth_date);
  if (!dateParts) {
    return "Birth date phai la ngay Gregorian hop le.";
  }

  if (!/^\d{2}:\d{2}$/.test(form.birth_time)) {
    return "Birth time phai co dinh dang HH:MM.";
  }

  const [hour, minute] = form.birth_time.split(":").map(Number);
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
    return "Birth time phai nam trong khoang 00:00-23:59.";
  }

  if (
    (form.chart_system === "BATU" || form.chart_system === "TUVI_BATU") &&
    (dateParts.year < BATU_SUPPORTED_YEAR_MIN || dateParts.year > BATU_SUPPORTED_YEAR_MAX)
  ) {
    return `Bat Tu chi ho tro nam ${BATU_SUPPORTED_YEAR_MIN}-${BATU_SUPPORTED_YEAR_MAX}.`;
  }

  return null;
}

async function calculateChartData(form: CreateChartFormState) {
  if (form.chart_system === "TUVI") {
    return calculateTuVi(form);
  }

  if (form.chart_system === "BATU") {
    return calculateBatTu(form);
  }

  const [tuvi, batu] = await Promise.all([calculateTuVi(form), calculateBatTu(form)]);
  return { tuvi, batu };
}

async function calculateTuVi(form: CreateChartFormState) {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!apiBaseUrl) {
    throw new Error("Thieu cau hinh NEXT_PUBLIC_API_BASE_URL cho Tu Vi engine.");
  }

  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/chart/tuvi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      label: form.label,
      birth_date: form.birth_date,
      birth_time: form.birth_time,
      gender: form.gender,
    }),
  });

  return parseEngineResponse(response, "Tu Vi");
}

async function calculateBatTu(form: CreateChartFormState) {
  const dateParts = parseBirthDate(form.birth_date);
  if (!dateParts) {
    throw new Error("Birth date khong hop le.");
  }

  const [hour] = form.birth_time.split(":").map(Number);
  const response = await fetch("/api/battu/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      year: dateParts.year,
      month: dateParts.month,
      day: dateParts.day,
      hour,
      gender: form.gender,
      label: form.label,
    }),
  });

  return parseEngineResponse(response, "Bat Tu");
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
    throw new Error(`${engineName} engine loi: ${message || response.statusText}`);
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
