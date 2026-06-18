import Link from "next/link";

export default function Home() {
  return (
    <main className="home-main">
      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-copy">
          <p className="auth-kicker">TuVi / BaTu GraphRAG</p>
          <h1 id="home-title">Lá số và tri thức mệnh lý</h1>
          <p>
            Hệ thống MVP hỗ trợ tạo, lưu và xem chart Tử Vi hoặc Bát Tự trong một giao
            diện rõ ràng, linh hoạt trên mọi kích thước màn hình.
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
            <h2>Tạo chart, đọc bảng, lưu lịch sử.</h2>
          </div>
          <p>
            Dashboard tập trung cho việc nhập thông tin sinh, chọn hệ thống chart và mở lại
            dữ liệu đã lưu khi cần đối chiếu.
          </p>
          <div className="system-strip" aria-hidden="true">
            <div className="system-row">
              <span>Visualizer</span>
              <strong>12 cung Tử Vi</strong>
            </div>
            <div className="system-row">
              <span>Calculator</span>
              <strong>Bốn trụ Bát Tự</strong>
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
