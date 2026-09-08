# Bản tin Marketing sáng — tự động qua Telegram (Bài 5)

## Hạ tầng đã dựng

| Thành phần | Giá trị |
|---|---|
| Tên bot | Ban tin marketing cua Trang |
| Username | `@ban_tin_marketing_trang_bot` |
| Token | ⚠️ Đã lộ — xem `BAO-MAT.md`, cần `/revoke` qua BotFather |
| Lịch chạy | **7h sáng hằng ngày, giờ Việt Nam** |
| Bản tin đầu tiên | 08/09/2026 |

## Cách tạo lại bot (nếu cần làm lại từ đầu)

1. Mở **Telegram**, bấm ô tìm kiếm 🔍 trên cùng
2. Gõ **BotFather** → bấm vào tài khoản có **dấu tích xanh** ✅ (đúng "ông tổ" tạo bot chính thức của Telegram)
3. Bấm nút **START** (hoặc gõ `/start`)
4. Gõ `/newbot`
5. BotFather hỏi **tên bot** — gõ gì cũng được, ví dụ `Ban tin Marketing cua Trang`
6. Hỏi tiếp **username** — bắt buộc kết thúc bằng `bot`, ví dụ `bantin_marketing_trang_bot`
   (nếu báo trùng, thêm vài số vào)
7. BotFather trả về dòng `Use this token to access the HTTP API:` — đó là "chìa khóa" của bot

**Bước bắt buộc sau đó**: Telegram không cho bot nhắn tin cho người dùng trước — Trang phải
"chào" nó một câu. Mở bot → bấm **START** (hoặc gõ `hi`) → Agent mới lấy được chat id để gửi tin.

## Cấu trúc bản tin (giữ nguyên format này)

Kiểu tin nhắn ngắn gọn, không dài dòng:

- **3 tin đáng chú ý** — mỗi tin kèm **1 dòng "Với bạn:"** giải nghĩa nó có nghĩa gì với người
  làm Marketing, kèm đường link nguồn
- **1 con số đáng nhớ** trong ngày
- **1 việc nên giao cho Agent** làm ngay hôm nay

### Ví dụ bản tin đã gửi (07/09/2026)

> **3 tin đáng chú ý**
> 1. Facebook mất thế độc quyền, TikTok tăng tốc (Google 28,4% · Meta 19,2% · TikTok 8,7%)
> 2. Nội dung "thật" (UGC) có tỷ lệ nhấp cao gấp 4 lần clip studio
> 3. Người Việt tìm kiếm ngay trên TikTok & Reels — video ngắn 15–30s lên ngôi
>
> **Con số đáng nhớ**: 79 triệu người Việt dùng mạng xã hội (84,2% dân số online)
>
> **Việc nên giao cho Agent hôm nay**: rà 10 bài blog SEO cũ → viết lại thành 10 hook video
> ngắn + caption có từ khoá cho TikTok/Reels

## Nguồn tin (chỉ lấy nguồn đáng tin)

- DataReportal — Digital 2026 Vietnam
- Advertising Vietnam
- The7 Digital

## Tùy chỉnh được

- Đổi giờ chạy
- Đổi giọng văn (nghiêm túc hơn / vui hơn / ngắn hơn)
- Thêm mảng quan tâm: SEO, Google Ads, TMĐT...
- Tắt bản tin bất cứ lúc nào
