---
name: thue-tncn-vietnam
description: Skill tra cứu Thuế Thu Nhập Cá Nhân (TNCN) Việt Nam 2026 - biểu thuế 5 bậc, giảm trừ gia cảnh, quyết toán, freelancer/KOL/seller. Căn cứ Luật 109/2025/QH15.
version: 1.2.0
author: Leo
updated: 2026-03-25
---

# Skill: thue-tncn-vietnam
**Phiên bản:** 1.2.0 | **Cập nhật:** 25/03/2026 | **Tác giả:** Leo

## Mô tả
Skill chuyên biệt về Thuế Thu Nhập Cá Nhân (TNCN) Việt Nam năm 2026, dựa trên Luật 109/2025/QH15 và các nghị quyết liên quan. Cung cấp thông tin có căn cứ pháp lý rõ ràng về biểu thuế 5 bậc, giảm trừ gia cảnh, quyết toán thuế, và hướng dẫn cho freelancer/KOL/người bán hàng online.

## Thay đổi lớn 2026
- **Biểu thuế 5 bậc** (rút từ 7 bậc) — Luật 109/2025/QH15, Điều 22
- **Giảm trừ gia cảnh tăng 40%**: bản thân 15,5 tr/tháng, NPT 6,2 tr/tháng — NQ 110/2025/UBTVQH15
- **Ngưỡng miễn thuế 500 triệu/năm** cho cá nhân kinh doanh — NQ 198/2025/QH15
- **Thuế khoán bị bãi bỏ** từ 01/01/2026
- **Sàn TMĐT khấu trừ thuế thay** từ 01/07/2025

---

## Hướng dẫn sử dụng Skill

### Khi nào dùng Skill này?
- Người dùng hỏi về thuế TNCN, biểu thuế, thuế suất
- Câu hỏi về giảm trừ gia cảnh, người phụ thuộc
- Hỏi về quyết toán thuế, deadline
- Freelancer, KOL, seller hỏi về nghĩa vụ thuế
- Câu hỏi về bán hàng online, sàn TMĐT
- Hỏi về thuế khoán (đã bãi bỏ), hộ kinh doanh

### Files tham chiếu
```
thue-tncn-vietnam/
├── SKILL.md                    ← File này (điểm vào chính)
└── references/
    ├── tong-quan-thue.md       ← Biểu thuế, giảm trừ, ngưỡng miễn thuế
    ├── vi-du-tinh-thue.md      ← 5 ví dụ tính thuế thực tế
    ├── sop-quyet-toan.md       ← SOP 9 bước quyết toán eTax Mobile
    ├── freelancer-guide.md     ← Hướng dẫn Freelancer/KOL/seller online
    ├── thue-khoan-guide.md     ← Thuế khoán & HKD (đã bãi bỏ, thông tin lịch sử)
    ├── deadline-tracker.md     ← Lịch nộp thuế 2026
    ├── faq.md                  ← 12 câu hỏi thường gặp có đáp án
    ├── system-flow.md          ← Sơ đồ quy trình & 3 Verification Gates
    ├── changelog.md            ← Lịch sử cập nhật
    └── sources.md              ← Nguồn tham khảo chính thống
```

### Luồng xử lý câu hỏi

```
1. NHẬN câu hỏi thuế TNCN
2. GATE 1 - Freshness Check: Dữ liệu có cập nhật 2026 không?
3. ĐỌC file reference liên quan
4. GATE 2 - Cross-Verify: So sánh câu trả lời với dữ liệu
5. GATE 3 - Source Citation: Thêm căn cứ pháp lý
6. TRẢ LỜI kèm disclaimer
```

---

## 5 Quy tắc Anti-Hallucination (BẮT BUỘC)

> ⛔ **RULE 1:** CẤM bịa số liệu thuế — mọi con số PHẢI có trong reference files
> ⛔ **RULE 2:** CẤM khẳng định khi không chắc — dùng "theo dữ liệu hiện có" hoặc "cần xác nhận với CQT"
> ⛔ **RULE 3:** CẤM tự suy luận quy định mới ngoài phạm vi tài liệu
> ⛔ **RULE 4:** CẤM trả lời ngoài phạm vi thuế TNCN Việt Nam 2026
> ✅ **RULE 5:** MỌI con số PHẢI kèm căn cứ pháp lý (Luật/NQ/TT)

---

## 3 Verification Gates

| Gate | Tên | Nhiệm vụ |
|------|-----|----------|
| Gate 1 | Freshness Check | Kiểm tra dữ liệu còn mới không (2026?) |
| Gate 2 | Cross-Verify | So sánh câu trả lời với dữ liệu trong reference |
| Gate 3 | Source Citation | Buộc trích nguồn pháp lý + disclaimer |

---

## Quick Reference (Dữ liệu chốt 2026)

### Biểu thuế lũy tiến 5 bậc (Luật 109/2025/QH15, Điều 22)
| Bậc | Thu nhập tính thuế/tháng | Thuế suất |
|-----|--------------------------|-----------|
| 1   | Đến 10 triệu             | 5%        |
| 2   | 10 – 30 triệu            | 10%       |
| 3   | 30 – 50 triệu            | 20%       |
| 4   | 50 – 80 triệu            | 25%       |
| 5   | Trên 80 triệu            | 35%       |

### Giảm trừ gia cảnh (NQ 110/2025/UBTVQH15)
| Đối tượng | Mức giảm trừ |
|-----------|-------------|
| Bản thân  | 15,5 triệu/tháng (186 triệu/năm) |
| Người phụ thuộc | 6,2 triệu/tháng/người |

### Ngưỡng doanh thu miễn thuế (NQ 198/2025/QH15)
| Doanh thu/năm | TNCN | GTGT |
|---------------|------|------|
| ≤ 500 triệu   | Miễn | Miễn |
| 500 tr – 3 tỷ | PP1: % DT **hoặc** PP2: theo lợi nhuận | % DT |
| > 3 tỷ        | Theo lợi nhuận (bắt buộc) | % DT (không phải lợi nhuận) |

---

## Disclaimer bắt buộc
> 📌 *Thông tin chỉ mang tính tham khảo, KHÔNG thay thế tư vấn thuế chuyên nghiệp. Căn cứ: Luật 109/2025/QH15, NQ 198/2025/QH15, NQ 110/2025/UBTVQH15. Kiểm tra tại: gdt.gov.vn*
