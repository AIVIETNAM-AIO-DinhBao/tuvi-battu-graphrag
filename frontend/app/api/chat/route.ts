import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

const CHAT_PROXY_TIMEOUT_MS = 30_000;

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get("authorization") ?? "";
  const accessToken = extractBearerToken(authHeader);

  if (!accessToken) {
    return jsonError("Bạn cần đăng nhập để đặt câu hỏi.", 401);
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!supabaseUrl || !supabaseAnonKey) {
    return jsonError("Thiếu cấu hình xác thực Supabase cho chat proxy.", 500);
  }

  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: userData, error: userError } = await supabase.auth.getUser(accessToken);
  if (userError || !userData.user) {
    return jsonError("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.", 401);
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return jsonError("Request chat không đúng định dạng JSON.", 400);
  }

  const chartId = readString(payload, "chart_id");
  const query = readString(payload, "query");
  const experimentConfigPath = readString(payload, "experiment_config_path");

  if (!chartId) {
    return jsonError("Thiếu chart_id cho câu hỏi.", 400);
  }
  if (!query) {
    return jsonError("Câu hỏi không được để trống.", 400);
  }

  const backendBaseUrl = process.env.BACKEND_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!backendBaseUrl) {
    return jsonError("Thiếu cấu hình BACKEND_API_BASE_URL cho chat proxy.", 500);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CHAT_PROXY_TIMEOUT_MS);

  try {
    const backendResponse = await fetch(`${backendBaseUrl.replace(/\/$/, "")}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        chart_id: chartId,
        query,
        user_id: userData.user.id,
        ...(experimentConfigPath ? { experiment_config_path: experimentConfigPath } : {}),
      }),
      signal: controller.signal,
    });

    const backendBody = await parseJsonSafely(backendResponse);
    if (!backendResponse.ok) {
      const status = backendResponse.status >= 500 ? 502 : backendResponse.status;
      const message = backendResponse.status >= 500
        ? "Không thể xử lý câu hỏi lúc này. Vui lòng thử lại sau."
        : extractErrorMessage(backendBody) ?? "Request chat không hợp lệ.";
      return jsonError(message, status);
    }

    if (!isRecord(backendBody) || typeof backendBody.answer !== "string") {
      return jsonError("Backend chat trả về dữ liệu không đúng định dạng.", 502);
    }

    return NextResponse.json({
      status: backendBody.status === "ok" ? "ok" : "ok",
      answer: backendBody.answer,
      sources: Array.isArray(backendBody.sources) ? backendBody.sources : [],
      trace: isRecord(backendBody.trace) ? backendBody.trace : {},
      experiment_id: typeof backendBody.experiment_id === "string" ? backendBody.experiment_id : null,
      config_hash: typeof backendBody.config_hash === "string" ? backendBody.config_hash : null,
      chunk_strategy_id: typeof backendBody.chunk_strategy_id === "string" ? backendBody.chunk_strategy_id : null,
      generation_metadata: isRecord(backendBody.generation_metadata) ? backendBody.generation_metadata : {},
      citation_metadata: isRecord(backendBody.citation_metadata) ? backendBody.citation_metadata : {},
    });
  } catch (error) {
    const message = error instanceof DOMException && error.name === "AbortError"
      ? "Chat backend phản hồi quá lâu. Vui lòng thử lại."
      : "Không thể kết nối chat backend lúc này.";
    return jsonError(message, 502);
  } finally {
    clearTimeout(timeoutId);
  }
}

function extractBearerToken(authHeader: string): string | null {
  const match = /^Bearer\s+(.+)$/i.exec(authHeader.trim());
  return match?.[1]?.trim() || null;
}

function readString(payload: unknown, key: string): string {
  if (!isRecord(payload)) {
    return "";
  }
  const value = payload[key];
  return typeof value === "string" ? value.trim() : "";
}

async function parseJsonSafely(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function extractErrorMessage(payload: unknown): string | null {
  if (!isRecord(payload)) {
    return null;
  }
  if (typeof payload.error === "string") return payload.error;
  if (typeof payload.detail === "string") return payload.detail;
  return null;
}

function jsonError(message: string, status: number) {
  return NextResponse.json({ error: message }, { status });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}