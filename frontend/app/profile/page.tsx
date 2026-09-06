"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

export default function ProfilePage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      const { data } = await supabase.auth.getSession();
      const user = data.session?.user;
      if (!user) {
        router.replace("/login");
        return;
      }

      const { data: profile, error } = await supabase
        .from("profiles")
        .select("display_name")
        .eq("id", user.id)
        .maybeSingle();

      if (cancelled) return;
      setEmail(user.email ?? "");
      if (error) {
        setError("Không thể tải hồ sơ lúc này. Vui lòng thử lại.");
      } else {
        setDisplayName(profile?.display_name ?? "");
      }
      setLoading(false);
    }

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setMessage(null);

    const { data } = await supabase.auth.getSession();
    const user = data.session?.user;
    if (!user) {
      router.replace("/login");
      return;
    }

    const { error } = await supabase.from("profiles").upsert({
      id: user.id,
      display_name: displayName.trim() || null,
    });
    setSaving(false);

    if (error) {
      setError("Không thể lưu hồ sơ lúc này. Vui lòng thử lại.");
      return;
    }
    setMessage("Hồ sơ đã được cập nhật.");
  }

  if (loading) {
    return <main className="loading-state">Đang tải hồ sơ...</main>;
  }

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>Hồ sơ của bạn</h1>
          <p>Cập nhật tên hiển thị dùng trong không gian lá số của bạn.</p>
        </div>
        <button type="button" className="secondary-button" onClick={() => router.push("/dashboard")}>
          Về lá số của bạn
        </button>
      </header>

      <section className="panel">
        <form className="chart-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input type="email" value={email} disabled />
          </label>
          <label>
            Tên hiển thị
            <input
              type="text"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="Ví dụ: Nguyễn Văn A"
              disabled={saving}
            />
          </label>
          <button type="submit" disabled={saving}>
            {saving ? "Đang lưu..." : "Lưu thay đổi"}
          </button>
          {error && <p className="error-message">{error}</p>}
          {message && <p className="notice-message">{message}</p>}
        </form>
      </section>
    </main>
  );
}
