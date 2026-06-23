import Link from "next/link";

export default function Home() {
  return (
    <main className="home-main">
      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-copy">
          <p className="auth-kicker">TuVi GraphRAG</p>
          <h1 id="home-title">Lá số Tử Vi và tri thức có nguồn</h1>
          <p>
            Hệ thống MVP hỗ trợ tạo, lưu và xem lá số Tử Vi trong một giao diện rõ ràng,
            linh hoạt trên mọi kích thước màn hình.
          </p>
          <div className="home-actions">
            <Link className="primary-link" href="/login">
              Đăng nhập
            </Link>
            <Link className="secondary-button" href="/register">
              Đăng ký
            </Link>
          </div>
        </div>

        <aside className="home-product-panel" aria-label="Các khả năng chính">
          <div>
            <p className="auth-kicker">Workspace</p>
            <h2>Tạo lá số, đọc bảng, lưu lịch sử.</h2>
          </div>
          <p>
            Dashboard tập trung cho việc nhập thông tin sinh, tạo lá số Tử Vi và mở lại dữ
            liệu đã lưu khi cần đối chiếu.
          </p>
          <div className="system-strip" aria-hidden="true">
            <div className="system-row">
              <span>Visualizer</span>
              <strong>12 cung Tử Vi</strong>
            </div>
            <div className="system-row">
              <span>Engine</span>
              <strong>Lá số Tử Vi</strong>
            </div>
            <div className="system-row">
              <span>Data</span>
              <strong>Supabase records</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
