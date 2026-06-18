"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const normalizedEmail = email.trim().toLowerCase();

    const { error } = await supabase.auth.signInWithPassword({
      email: normalizedEmail,
      password,
    });

    setLoading(false);
    if (error) {
      setError(getLoginErrorMessage(error.message));
      return;
    }

    router.push("/dashboard");
  };

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="login-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">TuVi / BaTu GraphRAG</p>
            <h1 id="login-title">Đăng nhập</h1>
            <p>Trở lại không gian lưu lá số, xem Tử Vi, Bát Tự và tiếp tục phân tích.</p>
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
                autoComplete="current-password"
                placeholder="Nhập mật khẩu"
                required
              />
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Đang đăng nhập..." : "Đăng nhập"}
            </button>

            {error && <p className="error-message">{error}</p>}
          </form>

          <p className="auth-footer">
            Chưa có tài khoản?{" "}
            <Link className="text-link" href="/register">
              Đăng ký
            </Link>
          </p>
        </div>

        <aside className="auth-side" aria-label="Tổng quan hệ thống">
          <div className="auth-side-content">
            <p className="auth-kicker">Hybrid knowledge workspace</p>
            <h2>Lá số rõ ràng, dữ liệu có ngữ cảnh.</h2>
            <p>
              Quản lý hồ sơ cá nhân, tạo chart Tử Vi hoặc Bát Tự, rồi mở chi tiết để xem
              trực quan theo từng cung, trụ và metadata đã lưu.
            </p>
          </div>

          <div className="auth-console" aria-hidden="true">
            <div className="auth-console-row">
              <span>Auth</span>
              <strong>Supabase session</strong>
            </div>
            <div className="auth-console-row">
              <span>Charts</span>
              <strong>Tử Vi + Bát Tự</strong>
            </div>
            <div className="auth-console-row">
              <span>View</span>
              <strong>Responsive boards</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function getLoginErrorMessage(message: string) {
  if (message.toLowerCase().includes("invalid login credentials")) {
    return "Email hoặc mật khẩu không đúng, hoặc tài khoản chưa xác nhận email. Nếu vừa đăng ký, hãy mở email xác nhận từ Supabase rồi đăng nhập lại.";
  }

  return message;
}
