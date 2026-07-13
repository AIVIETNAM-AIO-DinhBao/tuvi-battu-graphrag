"use client";

import type { CSSProperties, ReactNode } from "react";

export interface TuViStarDetail {
  name?: string;
  brightness?: string | null;
  brightness_code?: string | null;
  category?: string | null;
  color?: string | null;
  quality?: string | null;
  id?: number | string | null;
  is_luu?: boolean | null;
  source?: string | null;
  nam_xem_han?: number | null;
}

export interface TuViPalace {
  name?: string;
  stars?: string[];
  star_details?: TuViStarDetail[];
  star_groups?: Record<string, TuViStarDetail[]>;
  position?: number | null;
  attributes?: Record<string, unknown>;
}

export interface TuViChartData {
  chart_type?: string;
  version?: string;
  metadata?: {
    label?: string;
    birth_date?: string;
    birth_time?: string;
    gender?: string;
    nam_xem_han?: number;
    can_chi_nam_xem?: string;
    personal_info?: Record<string, unknown> | null;
    destiny_info?: Record<string, unknown> | null;
  };
  palaces?: Record<string, TuViPalace>;
  stars?: Record<string, unknown>;
  raw_data?: unknown;
}

interface TuViBoardProps {
  chart: TuViChartData;
}

interface NormalizedPalace {
  key: string;
  name: string;
  position: number;
  stars: TuViStarDetail[];
  attributes: Record<string, unknown>;
}

const PALACE_ORDER = [
  "Menh",
  "Phu Mau",
  "Phuc Duc",
  "Dien Trach",
  "Quan Loc",
  "No Boc",
  "Thien Di",
  "Tat Ach",
  "Tai Bach",
  "Tu Nu",
  "Phu The",
  "Huynh De",
];

const GRID_CELLS = [
  { x: 2, y: 3 },
  { x: 1, y: 3 },
  { x: 0, y: 3 },
  { x: 0, y: 2 },
  { x: 0, y: 1 },
  { x: 0, y: 0 },
  { x: 1, y: 0 },
  { x: 2, y: 0 },
  { x: 3, y: 0 },
  { x: 3, y: 1 },
  { x: 3, y: 2 },
  { x: 3, y: 3 },
];

const MAJOR_STAR_NAMES = new Set([
  "tu vi",
  "thien co",
  "thai duong",
  "vu khuc",
  "thien dong",
  "liem trinh",
  "thien phu",
  "thai am",
  "tham lang",
  "cu mon",
  "thien tuong",
  "thien luong",
  "that sat",
  "pha quan",
]);

const GOOD_STAR_NAMES = new Set([
  "thien khoi",
  "thien quy",
  "van xuong",
  "van khuc",
  "ta phu",
  "huu bat",
  "long tri",
  "phuong cac",
  "thai phu",
  "phong cao",
  "thien quan",
  "thien phuc",
  "thien duc",
  "nguyet duc",
  "an quang",
  "thien quyet",
  "hoa loc",
  "hoa quyen",
  "hoa khoa",
]);

const BAD_STAR_NAMES = new Set([
  "dia khong",
  "dia kiep",
  "kinh duong",
  "da la",
  "hoa tinh",
  "linh tinh",
  "kiep sat",
  "thien hinh",
  "thien rieu",
  "thien dieu",
  "dai hao",
  "tieu hao",
  "tang mon",
  "bach ho",
  "thien khoc",
  "thien hu",
  "thai tue",
  "phi liem",
  "thien khong",
  "luu ha",
  "thien la",
  "dia vong",
  "co than",
  "qua tu",
  "pha toai",
  "hoa ky",
]);

const TRANG_SINH_STAR_NAMES = new Set([
  "trang sinh",
  "truong sinh",
  "moc duc",
  "quan doi",
  "lam quan",
  "de vuong",
  "suy",
  "benh",
  "tu",
  "mo",
  "tuyet",
  "thai",
  "duong",
]);

export function TuViBoard({ chart }: TuViBoardProps) {
  const palaces = normalizePalaces(chart);
  const centerRows = buildCenterRows(chart);

  if (palaces.length !== 12) {
    return (
      <BoardMessage title="Không thể hiển thị bảng Tử Vi">
        Dữ liệu chart hiện có không đủ 12 cung.
      </BoardMessage>
    );
  }

  return (
    <section className="visualizer-section" aria-labelledby="tuvi-board-title">
      <div className="visualizer-heading">
        <div>
          <p className="eyebrow">Tử Vi</p>
          <h3 id="tuvi-board-title">Bảng 12 cung</h3>
        </div>
        <div className="visualizer-heading-meta">
          <p>
            {chart.metadata?.birth_date ?? "N/A"} - {chart.metadata?.birth_time ?? "N/A"}
          </p>
          <p className="visualizer-caption">Mỗi ô hiển thị Cung số, Đại hạn, Địa chi và các sao để dễ định vị nhanh.</p>
        </div>
      </div>

      <div className="tuvi-board-scroll">
        <div className="tuvi-board" role="img" aria-label="Bảng Tử Vi 12 cung">
          <section className="tuvi-center-cell" style={centerCellStyle()}>
            <h4>{truncateText(chart.metadata?.label ?? "Lá số Tử Vi", 32)}</h4>
            <dl className="tuvi-center-table">
              {centerRows.map((row, index) => (
                <div key={`${row.label}-${index}`}>
                  <dt>{row.label}</dt>
                  <dd title={row.value}>{truncateText(row.value, 34)}</dd>
                </div>
              ))}
            </dl>
          </section>

          {palaces.map((palace, index) => {
            const cell = GRID_CELLS[index];
            const starLayout = splitStars(palace.stars);
            const isHighlighted = isMenhOrThan(palace);
            const daiHan = textValue(
              palace.attributes.dai_han_age ?? palace.attributes.dai_han,
              "--",
            );
            const diaChi = textValue(palace.attributes.dia_chi, palace.key);
            const trangSinh = textValue(palace.attributes.trang_sinh, "");
            const tieuHan = textValue(palace.attributes.tieu_han, "");
            const luuNien = textValue(palace.attributes.luu_nien_dai_van, "");
            const khongVong = normalizeKhongVong(palace.attributes.khong_vong);

            return (
              <section
                className={isHighlighted ? "tuvi-palace-cell is-highlighted" : "tuvi-palace-cell"}
                key={`${palace.position}-${palace.key}`}
                style={cellStyle(cell.x, cell.y)}
                title={`${palace.name} - Cung ${palace.position}`}
              >
                <span className="tuvi-palace-age">ĐH {daiHan}</span>
                <span className="tuvi-palace-index">Cung {palace.position}</span>
                <span className="tuvi-palace-branch" title={diaChi}>
                  {truncateText(`Chi ${diaChi}`, 18)}
                </span>

                <h4 className="tuvi-palace-name">
                  <span>{palace.name}</span>
                  {khongVong.map((marker) => (
                    <span className="tuvi-khong-vong-badge" key={`${palace.key}-${marker}`}>
                      {marker}
                    </span>
                  ))}
                </h4>

                <div className="tuvi-major-stars">
                  {starLayout.major.map((star, starIndex) => (
                    <StarLine
                      className={starClassName(star, "major")}
                      key={`${palace.key}-major-${star.name}-${starIndex}`}
                      star={star}
                    />
                  ))}
                </div>

                <div className="tuvi-minor-columns">
                  <div className="tuvi-star-column is-good">
                    {starLayout.good.map((star, starIndex) => (
                      <StarLine
                        className={starClassName(star, "minor")}
                        key={`${palace.key}-good-${star.name}-${starIndex}`}
                        star={star}
                      />
                    ))}
                  </div>
                  <div className="tuvi-star-column is-bad">
                    {starLayout.bad.map((star, starIndex) => (
                      <StarLine
                        className={starClassName(star, "minor")}
                        key={`${palace.key}-bad-${star.name}-${starIndex}`}
                        star={star}
                      />
                    ))}
                  </div>
                </div>

                {trangSinh && <strong className="tuvi-trang-sinh">{trangSinh}</strong>}

                <footer className="tuvi-palace-footer">
                  <span>{truncateText(tieuHan ? `TH: ${tieuHan}` : "TH: --", 16)}</span>
                  <span>{truncateText(luuNien ? `LN: ${luuNien}` : "", 16)}</span>
                </footer>
              </section>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function StarLine({
  className,
  star,
}: {
  className: string;
  star: TuViStarDetail;
}) {
  const text = formatStar(star);
  return (
    <span className={className} title={text}>
      {text}
    </span>
  );
}

function centerCellStyle(): CSSProperties {
  return {
    gridColumn: "2 / span 2",
    gridRow: "2 / span 2",
  };
}

function cellStyle(x: number, y: number): CSSProperties {
  return {
    gridColumn: x + 1,
    gridRow: y + 1,
  };
}

function normalizePalaces(chart: TuViChartData): NormalizedPalace[] {
  const entries = Object.entries(chart.palaces ?? {});
  if (entries.length === 0) {
    return [];
  }

  const normalized = entries.map(([key, palace], index) => ({
    key,
    name: palace.name || key || PALACE_ORDER[index] || `Cung ${index + 1}`,
    position: normalizePosition(palace.position, index),
    stars: normalizeStars(palace),
    attributes: palace.attributes ?? {},
  }));

  const withUniquePositions = normalized.every(
    (palace, _index, all) =>
      palace.position >= 1 &&
      palace.position <= 12 &&
      all.filter((item) => item.position === palace.position).length === 1,
  );

  const ordered = withUniquePositions
    ? [...normalized].sort((a, b) => a.position - b.position)
    : normalized.map((palace, index) => ({ ...palace, position: index + 1 }));

  return ordered.slice(0, 12);
}

function normalizeStars(palace: TuViPalace): TuViStarDetail[] {
  const grouped = palace.star_groups;
  if (grouped) {
    return [
      ...(grouped.chinh_tinh ?? []),
      ...(grouped.phu_tinh ?? []),
      ...(grouped.khac ?? []),
    ].filter((star) => Boolean(star.name) && !isTrangSinhStar(star));
  }

  if (Array.isArray(palace.star_details) && palace.star_details.length > 0) {
    return palace.star_details.filter((star) => Boolean(star.name) && !isTrangSinhStar(star));
  }

  return (palace.stars ?? [])
    .filter(Boolean)
    .map((name) => ({ name }))
    .filter((star) => !isTrangSinhStar(star));
}

function splitStars(stars: TuViStarDetail[]) {
  const major = stars.filter(isMajorStar);
  const minor = stars.filter((star) => !isMajorStar(star));
  const goodMinor = minor.filter((star) => starQuality(star) !== "bad");
  const badMinor = minor.filter((star) => starQuality(star) === "bad");

  return {
    major,
    good: goodMinor,
    bad: badMinor,
  };
}

function buildCenterRows(chart: TuViChartData) {
  const metadata = chart.metadata ?? {};
  const personal = metadata.personal_info ?? {};
  const destiny = metadata.destiny_info ?? {};
  const solarDate = recordValue(personal, "solarDate");
  const lunarDate = recordValue(personal, "lunarDate");
  const birthHour = recordValue(personal, "birthHour");
  const canChi = recordValue(personal, "canChi");

  return [
    {
      label: "Năm xem hạn",
      value: [
        textValue(metadata.nam_xem_han, ""),
        textValue(metadata.can_chi_nam_xem, ""),
      ].filter(Boolean).join(" - ") || "Đang tính",
    },
    { label: "Dương lịch", value: formatDateObject(solarDate) || metadata.birth_date || "Đang tính" },
    { label: "Âm lịch", value: formatDateObject(lunarDate) || "Đang tính" },
    { label: "Giờ sinh", value: formatHour(birthHour, metadata.birth_time ?? "Đang tính") },
    { label: "Giới tính", value: textValue(personal.gender, metadata.gender ?? "Đang tính") },
    { label: "Âm dương", value: textValue(personal.amDuong, "Đang tính") },
    { label: "Âm dương lý", value: textValue(destiny.amDuongLy, "Đang tính") },
    { label: "Can chi năm", value: textValue(recordValue(canChi, "year"), "Đang tính") },
    { label: "Bản mệnh", value: textValue(destiny.banMenh, "Đang tính") },
    { label: "Cục mệnh", value: textValue(destiny.cucMenh, "Đang tính") },
    { label: "Cục - Mệnh", value: textValue(destiny.menhCucTuongQuan, "Đang tính") },
    {
      label: "Chủ mệnh/thân",
      value: [textValue(destiny.chuMenh, ""), textValue(destiny.chuThan, "")]
        .filter(Boolean)
        .join(" / ") || "Đang tính",
    },
    { label: "Cân lượng", value: textValue(destiny.canLuong, "Đang tính") },
    { label: "Thân cư", value: textValue(destiny.thanCu, "Đang tính") },
    { label: "Lai nhân", value: textValue(destiny.laiNhanCung, "Đang tính") },
  ];
}

function normalizePosition(position: number | null | undefined, fallbackIndex: number) {
  return typeof position === "number" && Number.isFinite(position) ? position : fallbackIndex + 1;
}

function isMenhOrThan(palace: NormalizedPalace) {
  const name = normalizeStarName(palace.name);
  const attrValues = Object.values(palace.attributes).map((value) =>
    normalizeStarName(String(value)),
  );

  return (
    name.includes("menh") ||
    name.includes("than") ||
    attrValues.some((value) => value.includes("menh") || value.includes("than"))
  );
}

function isMajorStar(star: TuViStarDetail) {
  const category = normalizeStarName(String(star.category ?? ""));
  if (category.includes("chinh")) {
    return true;
  }
  return MAJOR_STAR_NAMES.has(normalizeStarName(star.name ?? ""));
}

function starQuality(star: TuViStarDetail) {
  const explicit = normalizeStarName(String(star.quality ?? ""));
  if (explicit.includes("sat") || explicit.includes("bad") || explicit.includes("bai")) {
    return "bad";
  }
  if (explicit.includes("cat") || explicit.includes("good")) {
    return "good";
  }

  const name = normalizeStarLookup(star.name ?? "");
  if (BAD_STAR_NAMES.has(name)) {
    return "bad";
  }
  if (GOOD_STAR_NAMES.has(name)) {
    return "good";
  }
  return "good";
}

function isTrangSinhStar(star: TuViStarDetail) {
  return TRANG_SINH_STAR_NAMES.has(normalizeStarLookup(star.name ?? ""));
}

function formatStar(star: TuViStarDetail) {
  const name = star.name ?? "";
  const code = star.brightness_code;
  return code ? `${name} (${code})` : name;
}

function starClassName(star: TuViStarDetail, size: "major" | "minor") {
  const color = normalizeStarName(String(star.color ?? ""));
  const classes = ["tuvi-star", size === "major" ? "is-primary" : "is-secondary"];
  if (star.is_luu || normalizeStarName(star.name ?? "").startsWith("l ")) {
    classes.push("is-luu");
  }
  if (starQuality(star) === "bad") {
    classes.push("is-bad");
  } else {
    classes.push("is-good");
  }
  if (color.includes("strong")) {
    classes.push("is-strong");
  } else if (color.includes("weak")) {
    classes.push("is-weak");
  }
  return classes.join(" ");
}

function recordValue(value: unknown, key: string): unknown {
  if (isRecord(value)) {
    return value[key];
  }
  return undefined;
}

function formatDateObject(value: unknown) {
  if (!isRecord(value)) {
    return "";
  }
  const day = value.day ?? value.ngay;
  const month = value.month ?? value.thang;
  const year = value.year ?? value.nam;
  if (!day || !month || !year) {
    return "";
  }
  const leap = value.leap_month ? " nhuận" : "";
  return `${day}/${month}/${year}${leap}`;
}

function formatHour(value: unknown, fallback?: string) {
  if (!isRecord(value)) {
    return fallback ?? "N/A";
  }
  const branch = textValue(value.dia_chi, "");
  const range = textValue(value.range, "");
  return [branch, range].filter(Boolean).join(" ") || fallback || "N/A";
}

function textValue(value: unknown, fallback = "") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function normalizeKhongVong(value: unknown) {
  if (Array.isArray(value)) {
    return value.map((item) => textValue(item, "")).filter(Boolean);
  }
  const text = textValue(value, "");
  return text ? [text] : [];
}

function normalizeStarName(value: string) {
  return stripAccents(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function normalizeStarLookup(value: string) {
  const normalized = normalizeStarName(value);
  return normalized.startsWith("l ") ? normalized.slice(2).trim() : normalized;
}

function stripAccents(value: string) {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function truncateText(value: string, maxLength: number) {
  return value.length > maxLength ? `${value.slice(0, maxLength - 1)}...` : value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function BoardMessage({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="visualizer-section">
      <div className="board-message">
        <h3>{title}</h3>
        <p>{children}</p>
      </div>
    </section>
  );
}
