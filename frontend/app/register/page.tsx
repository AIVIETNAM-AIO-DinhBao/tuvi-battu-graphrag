"use client";

import { FormEvent, useState } from "react";
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
      "Tai khoan da duoc tao nhung can xac nhan email truoc khi dang nhap. Hay mo email xac nhan tu Supabase, roi quay lai dang nhap.",
    );
  };

  return (
    <main>
      <h1>Đăng ký</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </label>
        <label>
          Mật khẩu
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={6}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Đang tạo tài khoản..." : "Đăng ký"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {notice && <p style={{ color: "#166534" }}>{notice}</p>}
    </main>
  );
}
