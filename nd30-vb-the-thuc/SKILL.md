---
name: nd30-vb-the-thuc
description: Skill tạo văn bản hành chính đúng thể thức Nghị định 30/2020/NĐ-CP. Sinh file .docx pixel-perfect cho công văn và quyết định, với ma trận phân quyền ký TM/KT/TL tự động.
version: 1.0.0
author: Leo
updated: 2026-03-26
---

# Skill: Thể Thức Văn Bản Hành Chính — NĐ30
**Phiên bản:** 1.0 | **Tác giả:** Leo | **Chuẩn:** Nghị định 30/2020/NĐ-CP

## Mô tả
Skill này dạy AI Agent cách sinh file `.docx` văn bản hành chính đúng thể thức theo Nghị định 30/2020/NĐ-CP và Quyết định 4114/QĐ-BTC. Hỗ trợ 2 loại văn bản: **Công văn** (không có tên loại) và **Quyết định** (có tên loại).

## Yêu cầu hệ thống
| Thành phần | Yêu cầu |
|-----------|---------|
| Node.js | Phiên bản 18 trở lên |
| npm | Đi kèm Node.js |
| Thư viện docx | Phiên bản 9.0 trở lên (cài tự động) |
| Microsoft Word | Để mở và kiểm tra file .docx đầu ra |

## Cấu trúc thư mục
```
nd30-vb-the-thuc/
├── SKILL.md                     ← File này (hướng dẫn cho AI Agent)
├── package.json                 ← Khai báo thư viện docx
├── scripts/
│   ├── generate_cong_van.js     ← Script sinh công văn
│   └── generate_quyet_dinh.js   ← Script sinh quyết định
└── references/
    ├── quy_tac_the_thuc.md      ← Thông số pixel-perfect
    └── phan_quyen_ky.md         ← Ma trận phân quyền ký
```

## Cài đặt
```bash
# Vào thư mục skill
cd nd30-vb-the-thuc

# Cài thư viện
npm install
```

---

## Quy trình 5 bước (áp dụng cho cả 2 loại văn bản)

| Bước | Mô tả | Chi tiết |
|------|-------|---------|
| 1 | Thu thập thông tin | Hỏi: loại văn bản, cơ quan, người nhận, nội dung, ai ký |
| 2 | Tra phân quyền ký | Đọc `references/phan_quyen_ky.md` → xác định TM/KT/TL |
| 3 | Tạo file JSON | Tạo dữ liệu đầu vào theo cấu trúc quy định |
| 4 | Chạy script | Chạy lệnh node tương ứng |
| 5 | Kiểm tra | Mở file .docx bằng Word, kiểm tra header, font, lề |

---

## Hỗ trợ 2 loại văn bản

### CÔNG VĂN — Văn bản không có tên loại
Dùng khi trao đổi, hướng dẫn, đề nghị giữa các cơ quan. Không có tiêu đề "CÔNG VĂN" trên văn bản. Phần "Kính gửi" nằm ngay sau header.

**Lệnh chạy:**
```bash
node scripts/generate_cong_van.js --input data.json --output cong_van.docx
```

**JSON mẫu:**
```json
{
  "loai_van_ban": "cong_van",
  "co_quan_chu_quan": "BỘ TÀI CHÍNH",
  "co_quan_ban_hanh": "CỤC THUẾ TP. HÀ NỘI",
  "don_vi_soan_thao": "CT-HNi",
  "dia_danh": "Hà Nội",
  "trich_yeu": "V/v hướng dẫn kê khai thuế TNCN năm 2026",
  "kinh_gui": ["Các Chi cục Thuế quận, huyện"],
  "noi_dung": "Nội dung công văn...",
  "cap_ky": "KT",
  "chuc_vu_cap_tren": "CỤC TRƯỞNG",
  "chuc_vu_ky": "PHÓ CỤC TRƯỞNG",
  "nguoi_ky": "Nguyễn Văn An",
  "noi_nhan": ["- Như trên;", "- Cục trưởng (để b/c);", "- Lưu: VT, TNCN (3b)."]
}
```

### QUYẾT ĐỊNH — Văn bản có tên loại
Dùng khi ban hành quyết định hành chính: bổ nhiệm, thành lập tổ công tác, phê duyệt kế hoạch. Có tiêu đề "QUYẾT ĐỊNH" in hoa đậm giữa trang, phần "Căn cứ" in nghiêng, nội dung chia theo Điều.

**Lệnh chạy:**
```bash
node scripts/generate_quyet_dinh.js --input data.json --output quyet_dinh.docx
```

**JSON mẫu:**
```json
{
  "loai_van_ban": "quyet_dinh",
  "co_quan_chu_quan": "BỘ TÀI CHÍNH",
  "co_quan_ban_hanh": "CỤC THUẾ TP. HÀ NỘI",
  "don_vi_soan_thao": "QĐ-CT",
  "trich_yeu": "Về việc thành lập Tổ công tác kiểm tra thuế",
  "can_cu": [
    "Luật Quản lý thuế số 38/2019/QH14",
    "Nghị định số 126/2020/NĐ-CP ngày 19/10/2020"
  ],
  "noi_dung": "Điều 1. Thành lập Tổ công tác...\nĐiều 2. Tổ công tác có nhiệm vụ...\nĐiều 3. Quyết định này có hiệu lực kể từ ngày ký.",
  "cap_ky": "TM",
  "chuc_vu_ky": "CỤC TRƯỞNG",
  "nguoi_ky": "Phạm Đình Hưng",
  "noi_nhan": ["- Như Điều 3;", "- Phòng KT1, KT2;", "- Lưu: VT, TCCB (5b)."]
}
```

---

## Checklist kiểm tra sau khi tạo file

| Kiểm tra | Đúng | Sai thường gặp |
|---------|------|---------------|
| Header 2 cột | Table ẩn viền, cân đối | Dùng Tab/Space, bị lệch khi in |
| Quốc hiệu | Đủ chữ "NAM" trên 1 dòng | Chữ "NAM" rớt xuống dòng 2 |
| Gạch ngang | Border Top, chiều dài cố định | Dùng Underline, bị lệch |
| Font | Times New Roman toàn bộ | Lẫn font khác (Calibri, Arial) |
| Cỡ chữ | 13–14pt body, đúng từng phần | Cỡ đồng nhất, không phân biệt |
| Lề | Trái 3cm, các lề khác 2cm | Lề đều 2cm hoặc 2.54cm |
| Giãn dòng | Chính xác 17pt | Dùng Single hoặc 1.5 |
| Khối chữ ký | TM/KT/TL + chức vụ đúng | Thiếu tiền tố quyền hạn |

---

## Ví dụ câu lệnh tự nhiên cho AI Agent

- *"Soạn công văn gửi Sở Tài chính về việc hướng dẫn quyết toán thuế"*
- *"Tạo quyết định thành lập tổ công tác kiểm tra"*
- *"Soạn văn bản hành chính gửi các chi cục thuế"*

Agent sẽ tự động: **thu thập thông tin → tra phân quyền ký → tạo JSON → chạy script → xuất file .docx**

---

*Chuẩn áp dụng: Nghị định 30/2020/NĐ-CP | Quyết định 4114/QĐ-BTC | Công nghệ: Node.js + docx-js*
