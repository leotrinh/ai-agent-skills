# Quy Tắc Thể Thức Văn Bản Hành Chính — Thông Số Pixel-Perfect
**Chuẩn:** Nghị định 30/2020/NĐ-CP | Quyết định 4114/QĐ-BTC
**Cập nhật:** 26/03/2026

---

## 1. Khổ giấy và lề

| Thông số | Giá trị | Đơn vị dxa |
|---------|---------|-----------|
| Khổ giấy | A4 (210 × 297 mm) | — |
| Lề trái | 30 mm | ~1701 dxa |
| Lề phải | 20 mm | ~1134 dxa |
| Lề trên | 20 mm | ~1134 dxa |
| Lề dưới | 20 mm | ~1134 dxa |
| Font mặc định | Times New Roman, Unicode | — |

---

## 2. Header — Table 2 cột × 2 dòng (ẩn viền)

> ⚠️ **QUAN TRỌNG NHẤT:** Header PHẢI dùng **Table ẩn viền**, KHÔNG dùng Tab hay Space.

### Cấu trúc Header

```
+---------------------------+------------------------------------------+
| DÒNG 1 - CỘT TRÁI (3500) | DÒNG 1 - CỘT PHẢI (5571)                |
| - Tên cơ quan chủ quản   | - QUỐC HIỆU (in hoa, đậm, cỡ 13)       |
| - TÊN CƠ QUAN BAN HÀNH   | - Tiêu ngữ (đậm, thường, cỡ 14)        |
|   + Gạch ngang 1/3       |   + Gạch ngang = chiều dài tiêu ngữ    |
+---------------------------+------------------------------------------+
| DÒNG 2 - CỘT TRÁI (3500) | DÒNG 2 - CỘT PHẢI (5571)               |
| - Số, Ký hiệu            | - Địa danh, ngày tháng (nghiêng, cỡ 14)|
| - V/v (Trích yếu, cỡ 12) |                                         |
+---------------------------+------------------------------------------+
```

**Tỷ lệ cột:** `3500 : 5571` dxa
- Cột trái: 3500 dxa (~6.17 cm)
- Cột phải: 5571 dxa (~9.82 cm)
- Tổng: 9071 dxa (~16 cm) — đảm bảo "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" không rớt chữ "NAM"

### Thông số chi tiết từng yếu tố Header

| Yếu tố | Vị trí | Cỡ chữ | Kiểu | Gạch dưới |
|--------|--------|--------|------|----------|
| Quốc hiệu | Dòng 1, Cột phải | 13 | ĐẬM, IN HOA | Không |
| Tiêu ngữ | Dòng 1, Cột phải (dưới QH) | 14 | Đậm, Thường | Border Top, indent 1100 dxa |
| Cơ quan chủ quản | Dòng 1, Cột trái | 13 | Thường, IN HOA | Không |
| Cơ quan ban hành | Dòng 1, Cột trái (giữa) | 13 | ĐẬM, IN HOA | Border Top, indent 1350 dxa |
| Số, Ký hiệu | Dòng 2, Cột trái | 13 | Thường | Không |
| Địa danh, ngày tháng | Dòng 2, Cột phải | 14 | Nghiêng | Không |
| Trích yếu (V/v) | Dòng 2, Cột trái | 12 | Thường | Không |

---

## 3. Kỹ thuật gạch ngang — Border Top (BẮT BUỘC)

> ⛔ **TUYỆT ĐỐI KHÔNG** dùng `UnderlineType`, `ImageRun`, hay thẻ `<v:line>`

**Lý do:** UnderlineType phụ thuộc vào nội dung text, khi in sẽ bị lệch. Border Top là đường viền cố định của Paragraph, không phụ thuộc text.

```javascript
// Gạch dưới tên cơ quan ban hành (1/3 chiều rộng cột trái)
new Paragraph({
  spacing: { before: 20, after: 0 },
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }
  },
  indent: { left: 1350, right: 1350 }
});

// Gạch dưới tiêu ngữ (bằng chiều dài chữ)
new Paragraph({
  spacing: { before: 20, after: 0 },
  border: {
    top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }
  },
  indent: { left: 1100, right: 1100 }
});
```

---

## 4. Body — Thông số khoảng cách

| Thông số | Giá trị | Đơn vị twips |
|---------|---------|-------------|
| Khoảng cách trước đoạn | 6pt | 120 twips |
| Khoảng cách sau đoạn | 6pt | 120 twips |
| Giãn dòng | Chính xác 17pt | 340 twips (`LineRuleType.EXACT`) |
| Lùi đầu dòng | 1–1.27 cm | ~720 twips |
| Cỡ chữ body | 14 (hoặc 13) | — |
| Căn lề | Đều 2 bên (Justified) | — |

---

## 5. Khối chữ ký — Thông số kỹ thuật

| Yếu tố | Cỡ chữ | Kiểu |
|--------|--------|------|
| Quyền hạn (TM./KT./TL./TUQ.) | 13 | IN HOA, Đậm, căn phải |
| Chức vụ | 13 hoặc 14 | IN HOA, Đậm, căn giữa khối |
| "(Ký, ghi rõ họ tên)" | 14 | Nghiêng, căn giữa |
| Họ tên người ký | 14 | Đậm, căn giữa dưới chức vụ |
| Khoảng cách đến chữ ký | 2–3 dòng trống | — |

---

## 6. Nơi nhận — Thông số

| Yếu tố | Cỡ chữ | Kiểu |
|--------|--------|------|
| "Nơi nhận:" | 12 | Đậm, Nghiêng |
| Các mục liệt kê | 11 | Thường, bắt đầu bằng dấu "-" |
| Mục cuối | 11 | "Lưu: VT, ..." |

---

## 7. Khác biệt Công văn vs Quyết định

| Yếu tố | Công văn | Quyết định |
|--------|---------|-----------|
| Tên loại | Không có | "QUYẾT ĐỊNH" in hoa, đậm, giữa trang |
| Trích yếu | "V/v ..." cỡ 12, dưới số ký hiệu | Dưới tên loại, đậm, có gạch ngang |
| Căn cứ | Không có | Liệt kê căn cứ pháp lý, in nghiêng |
| Nội dung | Đoạn văn tự do | Chia theo Điều 1, Điều 2, Điều 3... |
| Kính gửi | Có | Không (thay bằng "Căn cứ") |

---

## 8. Câu hỏi thường gặp

**Tại sao dùng Border Top thay vì Underline?**
UnderlineType gắn vào text, khi text thay đổi thì đường gạch thay đổi. Border Top là đường viền của Paragraph, chiều dài cố định bằng indent, không phụ thuộc nội dung text.

**Tỷ lệ 3500:5571 nghĩa là gì?**
Chiều rộng 2 cột header tính bằng đơn vị dxa (1 inch = 1440 dxa). Tỷ lệ này đảm bảo "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" không bị rớt chữ "NAM" xuống dòng mới.

**Có thể thêm loại văn bản khác không?**
Có. Tạo script mới (VD: `generate_to_trinh.js`) theo cùng cấu trúc. Header và chữ ký giống nhau, chỉ khác phần Body.

---

*Nguồn: Nghị định 30/2020/NĐ-CP | Quyết định 4114/QĐ-BTC*
