-- Bài 13: micro-phễu hành vi + bản ghi phân tích của AI

CREATE TABLE IF NOT EXISTS su_kien (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  buoc       TEXT NOT NULL,          -- vao_trang | cuon_qua_form | cham_form | bam_gui
  nguon      TEXT,
  la_mau     INTEGER NOT NULL DEFAULT 0,   -- 1 = dữ liệu mẫu, 0 = số thật
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sk_buoc ON su_kien(buoc);
CREATE INDEX IF NOT EXISTS idx_sk_mau  ON su_kien(la_mau);

CREATE TABLE IF NOT EXISTS phan_tich (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  probe_nonce   TEXT,
  ty_le_chuyen  REAL,
  goi_y_ai      TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_pt_nonce ON phan_tich(probe_nonce);
