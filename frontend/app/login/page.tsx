"use client";

import { FormEvent, useState } from "react";
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
    <main>
      <h1>Đăng nhập</h1>
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
            autoComplete="current-password"
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Đang đăng nhập..." : "Đăng nhập"}
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
    </main>
  );
}

function getLoginErrorMessage(message: string) {
  if (message.toLowerCase().includes("invalid login credentials")) {
    return "Email/mat khau khong dung, hoac tai khoan chua xac nhan email. Neu vua dang ky, hay mo email xac nhan tu Supabase truoc roi dang nhap lai.";
  }

  return message;
}
