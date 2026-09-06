"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabaseClient";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError("Mật khẩu mới cần có ít nhất 6 ký tự.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận chưa khớp.");
      return;
    }

    setLoading(true);
    const { error } = await supabase.auth.updateUser({ password });
    setLoading(false);

    if (error) {
      setError("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn. Hãy yêu cầu một liên kết mới.");
      return;
    }

    router.replace("/dashboard");
  }

  return (
    <main className="auth-main">
      <section className="auth-shell" aria-labelledby="reset-password-title">
        <div className="auth-panel">
          <div className="auth-copy">
            <p className="auth-kicker">Tử Vi</p>
            <h1 id="reset-password-title">Đặt mật khẩu mới</h1>
            <p>Chọn một mật khẩu mới để tiếp tục sử dụng tài khoản của bạn.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field-group">
              <label htmlFor="password">Mật khẩu mới</label>
              <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" minLength={6} required />
            </div>
            <div className="field-group">
              <label htmlFor="confirm-password">Xác nhận mật khẩu mới</label>
              <input id="confirm-password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" minLength={6} required />
            </div>
            <button type="submit" disabled={loading}>{loading ? "Đang cập nhật..." : "Lưu mật khẩu mới"}</button>
            {error && <p className="error-message">{error}</p>}
          </form>

          <p className="auth-footer">
            <Link className="text-link" href="/forgot-password">Yêu cầu liên kết mới</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
