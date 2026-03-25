# Sơ Đồ Quy Trình & Verification Gates
**Cập nhật:** 25/03/2026

---

## 1. Luồng xử lý câu hỏi thuế TNCN

```
┌─────────────────────────────────────────┐
│          NHẬN CÂU HỎI THUẾ TNCN        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     GATE 1 — FRESHNESS CHECK           │
│  Dữ liệu có cập nhật 2026 không?       │
│  Luật 109/2025/QH15 đã áp dụng chưa?  │
└──────────────────┬──────────────────────┘
                   │ ✅ PASS
                   ▼
┌─────────────────────────────────────────┐
│     PHÂN LOẠI CÂU HỎI                  │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │ Biểu    │  │ Quyết   │  │ Free- │ │
│  │ Thuế/   │  │ Toán    │  │ lancer│ │
│  │ Giảm Trừ│  │ SOP     │  │ /KOL  │ │
│  └──────────┘  └──────────┘  └───────┘ │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     ĐỌC FILE REFERENCE PHÙ HỢP        │
│  • tong-quan-thue.md                   │
│  • vi-du-tinh-thue.md                  │
│  • sop-quyet-toan.md                   │
│  • freelancer-guide.md                 │
│  • faq.md                              │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     GATE 2 — CROSS-VERIFY              │
│  So sánh câu trả lời với dữ liệu?      │
│  Số liệu có trong reference không?     │
└──────────────────┬──────────────────────┘
                   │ ✅ PASS
                   ▼
┌─────────────────────────────────────────┐
│     GATE 3 — SOURCE CITATION           │
│  Thêm căn cứ pháp lý                  │
│  Thêm disclaimer                       │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│          TRẢ LỜI NGƯỜI DÙNG            │
└─────────────────────────────────────────┘
```

---

## 2. Decision Tree — Tôi thuộc nhóm nào?

```
Bạn có thu nhập từ đâu?
│
├─► Lương từ DN/tổ chức
│     │
│     ├─► 1 nơi: DN quyết toán thay được
│     └─► 2+ nơi: Bạn phải tự quyết toán
│
├─► Cá nhân kinh doanh (bán hàng, dịch vụ)
│     │
│     ├─► DT ≤ 500 tr/năm → MIỄN THUẾ
│     ├─► DT 500tr–3ty → Nộp % DT, kê khai quý
│     └─► DT > 3 tỷ → Cần sổ sách kế toán
│
├─► Freelancer / KOL
│     │
│     ├─► Tổng DT ≤ 500 tr/năm → MIỄN THUẾ
│     ├─► DN đã khấu trừ 10%? → Xin hoàn khi QT
│     └─► YouTube/FB → Tự kê khai
│
└─► Bán hàng sàn TMĐT
      │
      ├─► DT ≤ 500 tr → Sàn không khấu trừ
      └─► DT > 500 tr → Sàn khấu trừ thay 1,5%
```

---

## 3. Verification Gate — Chi tiết

### Gate 1: Freshness Check

**Mục đích:** Đảm bảo AI không dùng luật cũ (trước 2026).

**Kiểm tra:**
- Biểu thuế đang dùng có phải 5 bậc không? (2026 = 5 bậc, 2025 = 7 bậc)
- Ngưỡng miễn thuế có phải 500 tr không? (2026 = 500 tr, 2025 = 100 tr)
- Giảm trừ bản thân có phải 15,5 tr không? (2026 = 15,5 tr, 2025 = 11 tr)

**Nếu FAIL:** Cập nhật lại với dữ liệu 2026 từ reference files.

---

### Gate 2: Cross-Verify

**Mục đích:** Đảm bảo câu trả lời không bịa số liệu.

**Kiểm tra:**
- Mọi con số trong câu trả lời có xuất hiện trong reference files không?
- Có suy luận ngoài phạm vi tài liệu không?

**Nếu FAIL:** Từ chối trả lời phần đó và nói rõ "Không có trong dữ liệu hiện tại".

---

### Gate 3: Source Citation

**Mục đích:** Mọi câu trả lời thuế phải có căn cứ pháp lý.

**Format chuẩn:**
```
[Trả lời câu hỏi]

📌 Căn cứ: [Tên luật/NQ]
🔗 Kiểm tra tại: gdt.gov.vn
⚠️ Thông tin chỉ mang tính tham khảo, không thay thế tư vấn chuyên nghiệp.
```

---

## 4. 5 Anti-Hallucination Rules

```
RULE 1: ⛔ CẤM bịa số liệu thuế
         → Mọi con số PHẢI có trong reference files

RULE 2: ⛔ CẤM khẳng định khi không chắc
         → Dùng: "theo dữ liệu hiện có" hoặc
                  "cần xác nhận với CQT"

RULE 3: ⛔ CẤM tự suy luận quy định mới
         → Chỉ trả lời dựa trên tài liệu có sẵn

RULE 4: ⛔ CẤM trả lời ngoài phạm vi thuế TNCN VN 2026
         → Từ chối lịch sự và gợi ý nguồn phù hợp

RULE 5: ✅ MỌI con số PHẢI kèm căn cứ pháp lý
         → Luật/NQ/TT/Thông tư cụ thể
```

---

*Cập nhật: 25/03/2026 — Version 1.2.0*
