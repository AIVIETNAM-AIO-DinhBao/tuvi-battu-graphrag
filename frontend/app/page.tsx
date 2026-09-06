import Link from "next/link";

export default function Home() {
  return (
    <main className="home-main">
      <section className="home-hero" aria-labelledby="home-title">
        <div className="home-copy">
          <p className="auth-kicker">Tử Vi</p>
          <h1 id="home-title">Lá số Tử Vi của bạn</h1>
          <p>
            Tạo lá số, xem 12 cung và lưu lại những luận giải để xem lại bất cứ khi nào bạn cần.
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

        <aside className="home-product-panel" aria-label="Các chức năng chính">
          <div>
            <p className="auth-kicker">Cùng bạn chiêm nghiệm</p>
            <h2>Tạo lá số, xem 12 cung và lưu lịch sử.</h2>
          </div>
          <p>
            Nhập thông tin sinh để lập lá số Tử Vi, xem sơ đồ 12 cung và trò chuyện về lá số của bạn.
          </p>
          <div className="system-strip" aria-hidden="true">
            <div className="system-row">
              <span>Sơ đồ lá số</span>
              <strong>12 cung Tử Vi</strong>
            </div>
            <div className="system-row">
              <span>Luận giải</span>
              <strong>Phân tích lá số</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
