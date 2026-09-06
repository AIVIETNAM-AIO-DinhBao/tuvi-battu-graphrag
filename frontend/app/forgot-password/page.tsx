"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { supabase } from "../../lib/supabaseClient";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    const { error } = await supabase.auth.resetPasswordForEmail(email.trim().toLowerCase(), {
      redirectTo: typeof window !== "undefined" ? `${window.location.origin}/reset-password` : undefined,
    });
    setLoading(false);

    if (error) {
      setError("Không thể gửi email đặt lại mật khẩu. Vui lòng kiểm tra lại email và thử lại.");
      return;
    }

    setMessage("Nếu email đã đăng ký, hướng dẫn đặt lại mật khẩu sẽ được gửi đến hộp thư của bạn.");
  }

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="forgot-password-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">Tử Vi</p>
            <h1 id="forgot-password-title">Quên mật khẩu?</h1>
            <p>Nhập email đã đăng ký để nhận hướng dẫn đặt lại mật khẩu.</p>
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
                placeholder="NguyenVanA@gmail.com"
                required
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? "Đang gửi..." : "Gửi hướng dẫn"}
            </button>
            {error && <p className="error-message">{error}</p>}
            {message && <p className="notice-message">{message}</p>}
          </form>

          <p className="auth-footer">
            <Link className="text-link" href="/login">Quay lại đăng nhập</Link>
          </p>
        </div>

        <aside className="auth-side" aria-label="Hỗ trợ tài khoản">
          <div className="auth-side-content">
            <p className="auth-kicker">Hỗ trợ tài khoản</p>
            <h2>Tiếp tục hành trình cùng lá số của bạn.</h2>
            <p>Sau khi đặt lại mật khẩu, bạn có thể đăng nhập và xem lại những lá số đã lưu.</p>
          </div>
        </aside>
      </section>
    </main>
  );
}
