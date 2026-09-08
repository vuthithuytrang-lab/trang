CREATE TABLE IF NOT EXISTS leads (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  ho_ten      TEXT NOT NULL,
  sdt         TEXT NOT NULL,
  email       TEXT,
  nhu_cau     TEXT,
  ngan_sach   TEXT,
  nguon       TEXT,
  trang_thai  TEXT NOT NULL DEFAULT 'lead',
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_leads_hoten   ON leads(ho_ten);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);
