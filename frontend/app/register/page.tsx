"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setNotice(null);

    const normalizedEmail = email.trim().toLowerCase();

    const { data, error } = await supabase.auth.signUp({
      email: normalizedEmail,
      password,
      options: {
        emailRedirectTo:
          typeof window !== "undefined" ? `${window.location.origin}/dashboard` : undefined,
      },
    });

    setLoading(false);
    if (error) {
      setError(error.message);
      return;
    }

    if (data.session) {
      router.push("/dashboard");
      return;
    }

    setNotice(
      "Tài khoản đã được tạo nhưng cần xác nhận email trước khi đăng nhập. Hãy mở email xác nhận từ Supabase, rồi quay lại đăng nhập.",
    );
  };

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="register-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">TuVi / BaTu GraphRAG</p>
            <h1 id="register-title">Tạo tài khoản</h1>
            <p>Bắt đầu lưu chart cá nhân và mở lại các phân tích Tử Vi, Bát Tự khi cần.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                placeholder="ban@example.com"
                required
              />
            </div>

            <div className="field-group">
              <label htmlFor="password">Mật khẩu</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="new-password"
                minLength={6}
                placeholder="Tối thiểu 6 ký tự"
                required
              />
              <p className="field-hint">Dùng ít nhất 6 ký tự để đáp ứng cấu hình Supabase.</p>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Đang tạo tài khoản..." : "Đăng ký"}
            </button>

            {error && <p className="error-message">{error}</p>}
            {notice && <p className="notice-message">{notice}</p>}
          </form>

          <p className="auth-footer">
            Đã có tài khoản?{" "}
            <Link className="text-link" href="/login">
              Đăng nhập
            </Link>
          </p>
        </div>

        <aside className="auth-side" aria-label="Tổng quan hệ thống">
          <div className="auth-side-content">
            <p className="auth-kicker">Personal chart library</p>
            <h2>Một nơi gọn để giữ và đọc lá số.</h2>
            <p>
              Sau khi xác nhận email, bạn có thể tạo chart, lưu lịch sử và mở lại bảng
              trực quan trên mọi kích thước màn hình.
            </p>
          </div>

          <div className="auth-console" aria-hidden="true">
            <div className="auth-console-row">
              <span>Account</span>
              <strong>Email confirmation</strong>
            </div>
            <div className="auth-console-row">
              <span>Storage</span>
              <strong>Saved chart records</strong>
            </div>
            <div className="auth-console-row">
              <span>Engine</span>
              <strong>Hybrid calculations</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
