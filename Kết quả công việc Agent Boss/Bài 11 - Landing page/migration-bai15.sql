-- Bài 15: đánh dấu lead nào là dữ liệu mẫu, để báo cáo nói rõ đâu là số thật.
ALTER TABLE leads ADD COLUMN la_mau INTEGER NOT NULL DEFAULT 0;
