-- Bài 12: chấm MQL tự động + đếm lượt vào trang
ALTER TABLE leads ADD COLUMN is_mql INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS bo_dem (
  ten TEXT PRIMARY KEY,
  so  INTEGER NOT NULL DEFAULT 0
);
INSERT OR IGNORE INTO bo_dem (ten, so) VALUES ('traffic', 0);

CREATE TABLE IF NOT EXISTS luot_vao (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  nguon      TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_luotvao_nguon ON luot_vao(nguon);
CREATE INDEX IF NOT EXISTS idx_leads_mql     ON leads(is_mql);
CREATE INDEX IF NOT EXISTS idx_leads_nguon   ON leads(nguon);
