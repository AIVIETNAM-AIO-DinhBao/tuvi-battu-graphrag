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
  { x: 0, y: 0 },
  { x: 1, y: 0 },
  { x: 2, y: 0 },
  { x: 3, y: 0 },
  { x: 3, y: 1 },
  { x: 3, y: 2 },
  { x: 3, y: 3 },
  { x: 2, y: 3 },
  { x: 1, y: 3 },
  { x: 0, y: 3 },
  { x: 0, y: 2 },
  { x: 0, y: 1 },
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
  "co than",
  "qua tu",
  "pha toai",
  "hoa ky",
]);

const MAX_MAJOR_STARS = 3;
const MAX_MINOR_PER_COLUMN = 6;

export function TuViBoard({ chart }: TuViBoardProps) {
  const palaces = normalizePalaces(chart);
  const centerRows = buildCenterRows(chart);

  if (palaces.length !== 12) {
    return (
      <BoardMessage title="Khong the hien thi bang Tu Vi">
        Du lieu chart hien co khong du 12 cung.
      </BoardMessage>
    );
  }

  return (
    <section className="visualizer-section" aria-labelledby="tuvi-board-title">
      <div className="visualizer-heading">
        <div>
          <p className="eyebrow">Tu Vi</p>
          <h3 id="tuvi-board-title">Bang 12 cung</h3>
        </div>
        <p>
          {chart.metadata?.birth_date ?? "N/A"} - {chart.metadata?.birth_time ?? "N/A"}
        </p>
      </div>

      <div className="tuvi-board-scroll">
        <div className="tuvi-board" role="img" aria-label="Bang Tu Vi 12 cung">
          <section className="tuvi-center-cell" style={centerCellStyle()}>
            <h4>{truncateText(chart.metadata?.label ?? "La so Tu Vi", 32)}</h4>
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

            return (
              <section
                className={isHighlighted ? "tuvi-palace-cell is-highlighted" : "tuvi-palace-cell"}
                key={`${palace.position}-${palace.key}`}
                style={cellStyle(cell.x, cell.y)}
              >
                <span className="tuvi-palace-age">{daiHan}</span>
                <span className="tuvi-palace-branch" title={[diaChi, trangSinh].filter(Boolean).join(" - ")}>
                  {truncateText([diaChi, trangSinh].filter(Boolean).join(" - "), 24)}
                </span>

                <h4 className="tuvi-palace-name">{palace.name}</h4>

                <div className="tuvi-major-stars">
                  {starLayout.major.map((star, starIndex) => (
                    <StarLine
                      className={starClassName(star, "major")}
                      key={`${palace.key}-major-${star.name}-${starIndex}`}
                      maxLength={26}
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
                        maxLength={15}
                        star={star}
                      />
                    ))}
                  </div>
                  <div className="tuvi-star-column is-bad">
                    {starLayout.bad.map((star, starIndex) => (
                      <StarLine
                        className={starClassName(star, "minor")}
                        key={`${palace.key}-bad-${star.name}-${starIndex}`}
                        maxLength={15}
                        star={star}
                      />
                    ))}
                  </div>
                </div>

                {starLayout.overflowCount > 0 && (
                  <span className="tuvi-star-overflow">+{starLayout.overflowCount} sao</span>
                )}

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
  maxLength,
  star,
}: {
  className: string;
  maxLength: number;
  star: TuViStarDetail;
}) {
  const text = formatStar(star);
  return (
    <span className={className} title={text}>
      {truncateText(text, maxLength)}
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
    ].filter((star) => Boolean(star.name));
  }

  if (Array.isArray(palace.star_details) && palace.star_details.length > 0) {
    return palace.star_details.filter((star) => Boolean(star.name));
  }

  return (palace.stars ?? []).filter(Boolean).map((name) => ({ name }));
}

function splitStars(stars: TuViStarDetail[]) {
  const major = stars.filter(isMajorStar);
  const minor = stars.filter((star) => !isMajorStar(star));
  const goodMinor = minor.filter((star) => starQuality(star) !== "bad");
  const badMinor = minor.filter((star) => starQuality(star) === "bad");

  const visibleMajor = major.slice(0, MAX_MAJOR_STARS);
  const visibleGood = goodMinor.slice(0, MAX_MINOR_PER_COLUMN);
  const visibleBad = badMinor.slice(0, MAX_MINOR_PER_COLUMN);
  const overflowCount =
    major.length +
    minor.length -
    visibleMajor.length -
    visibleGood.length -
    visibleBad.length;

  return {
    major: visibleMajor,
    good: visibleGood,
    bad: visibleBad,
    overflowCount: Math.max(overflowCount, 0),
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
    { label: "Duong lich", value: formatDateObject(solarDate) || metadata.birth_date || "Dang tinh" },
    { label: "Am lich", value: formatDateObject(lunarDate) || "Dang tinh" },
    { label: "Gio sinh", value: formatHour(birthHour, metadata.birth_time ?? "Dang tinh") },
    { label: "Gioi tinh", value: textValue(personal.gender, metadata.gender ?? "Dang tinh") },
    { label: "Am duong", value: textValue(personal.amDuong, "Dang tinh") },
    { label: "Can chi nam", value: textValue(recordValue(canChi, "year"), "Dang tinh") },
    { label: "Ban menh", value: textValue(destiny.banMenh, "Dang tinh") },
    { label: "Cuc menh", value: textValue(destiny.cucMenh, "Dang tinh") },
    {
      label: "Chu menh/than",
      value: [textValue(destiny.chuMenh, ""), textValue(destiny.chuThan, "")]
        .filter(Boolean)
        .join(" / ") || "Dang tinh",
    },
    { label: "Can luong", value: textValue(destiny.canLuong, "Dang tinh") },
    { label: "Than cu", value: textValue(destiny.thanCu, "Dang tinh") },
    { label: "Lai nhan", value: textValue(destiny.laiNhanCung, "Dang tinh") },
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

  const name = normalizeStarName(star.name ?? "");
  if (BAD_STAR_NAMES.has(name)) {
    return "bad";
  }
  if (GOOD_STAR_NAMES.has(name)) {
    return "good";
  }
  return "good";
}

function formatStar(star: TuViStarDetail) {
  const name = star.name ?? "";
  const code = star.brightness_code;
  return code ? `${name} (${code})` : name;
}

function starClassName(star: TuViStarDetail, size: "major" | "minor") {
  const color = normalizeStarName(String(star.color ?? ""));
  const classes = ["tuvi-star", size === "major" ? "is-primary" : "is-secondary"];
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
  const leap = value.leap_month ? " nhuan" : "";
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

function normalizeStarName(value: string) {
  return stripAccents(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
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
