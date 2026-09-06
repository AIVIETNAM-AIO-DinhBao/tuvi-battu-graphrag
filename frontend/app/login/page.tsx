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

    try {
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: normalizedEmail,
        password,
      });

      if (signInError) {
        setError(getLoginErrorMessage(signInError.message));
        return;
      }

      router.replace("/dashboard");
    } catch {
      setError("Không thể kết nối đến dịch vụ đăng nhập. Hãy kiểm tra mạng rồi thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="login-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">Tử Vi</p>
            <h1 id="login-title">Đăng nhập</h1>
            <p>Trở lại không gian lưu lá số Tử Vi và tiếp tục phân tích.</p>
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
            <Link className="text-link" href="/forgot-password">
              Quên mật khẩu?
            </Link>
          </p>

          <p className="auth-footer">
            Chưa có tài khoản?{" "}
            <Link className="text-link" href="/register">
              Đăng ký
            </Link>
          </p>
        </div>

        <aside className="auth-side" aria-label="Không gian lá số">
          <div className="auth-side-content">
            <p className="auth-kicker">Lá số của bạn</p>
            <h2>Lưu lá số, xem luận giải khi cần.</h2>
            <p>
              Quản lý hồ sơ, tạo lá số Tử Vi và xem luận giải chi tiết, trực quan theo từng cung.
            </p>
          </div>

          <div className="auth-console" aria-hidden="true">
            <div className="auth-console-row">
              <span>Xác thực</span>
              <strong>Duy trì đăng nhập</strong>
            </div>
            <div className="auth-console-row">
              <span>Kho lưu trữ lá số</span>
              <strong>Lá số Tử Vi</strong>
            </div>
            <div className="auth-console-row">
              <span>Giao diện</span>
              <strong>Đa nền tảng</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function getLoginErrorMessage(message: string) {
  if (message.toLowerCase().includes("invalid login credentials")) {
    return "Email hoặc mật khẩu không đúng, hoặc tài khoản chưa xác nhận email. Nếu vừa đăng ký, hãy mở email xác nhận rồi đăng nhập lại.";
  }

  return message;
}
