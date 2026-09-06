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
  const [resendLoading, setResendLoading] = useState(false);

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

    setNotice("Tài khoản đã được tạo. Hãy kiểm tra hộp thư để xác nhận email trước khi đăng nhập.");
  };

  const handleResendConfirmation = async () => {
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail) {
      setError("Hãy nhập email trước khi gửi lại thư xác nhận.");
      return;
    }

    setResendLoading(true);
    setError(null);
    const { error } = await supabase.auth.resend({
      type: "signup",
      email: normalizedEmail,
      options: {
        emailRedirectTo:
          typeof window !== "undefined" ? `${window.location.origin}/dashboard` : undefined,
      },
    });
    setResendLoading(false);

    if (error) {
      setError("Không thể gửi lại email xác nhận lúc này. Vui lòng thử lại sau.");
      return;
    }

    setNotice("Email xác nhận mới đã được gửi. Hãy kiểm tra hộp thư đến và thư rác.");
  };

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="register-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">Tử Vi</p>
            <h1 id="register-title">Tạo tài khoản</h1>
            <p>Tạo tài khoản để lưu lá số và xem lại các luận giải của riêng bạn.</p>
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
                autoComplete="new-password"
                minLength={6}
                placeholder="Tối thiểu 6 ký tự"
                required
              />
              <p className="field-hint">Đặt mật khẩu ít nhất 6 ký tự để bảo vệ tài khoản của bạn.</p>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Đang tạo tài khoản..." : "Đăng ký"}
            </button>

            {error && <p className="error-message">{error}</p>}
            {notice && (
              <div className="notice-message">
                <p>{notice}</p>
                <button type="button" className="secondary-button" disabled={resendLoading} onClick={handleResendConfirmation}>
                  {resendLoading ? "Đang gửi lại..." : "Gửi lại email xác nhận"}
                </button>
              </div>
            )}
          </form>

          <p className="auth-footer">
            Đã có tài khoản?{" "}
            <Link className="text-link" href="/login">
              Đăng nhập
            </Link>
          </p>
        </div>

        <aside className="auth-side" aria-label="Thông tin tài khoản">
          <div className="auth-side-content">
            <p className="auth-kicker">Lưu lại hành trình của bạn</p>
            <h2>Một nơi gọn để giữ và đọc lá số.</h2>
            <p>
              Sau khi xác nhận email, bạn có thể tạo lá số, lưu lịch sử và xem lại những lần luận giải.
            </p>
          </div>

          <div className="auth-console" aria-hidden="true">
            <div className="auth-console-row">
              <span>Hội viên</span>
              <strong>Xác nhận email</strong>
            </div>
            <div className="auth-console-row">
              <span>Không gian lưu trữ</span>
              <strong>Quản lý lá số</strong>
            </div>
            <div className="auth-console-row">
              <span>Bộ phân tích</span>
              <strong>Lập lá số</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
