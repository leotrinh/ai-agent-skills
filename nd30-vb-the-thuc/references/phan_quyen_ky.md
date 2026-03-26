# Ma Trận Phân Quyền Ký Văn Bản Hành Chính
**Chuẩn:** Nghị định 30/2020/NĐ-CP
**Cập nhật:** 26/03/2026

---

## 1. Các hình thức ký

| Viết tắt | Đầy đủ | Ý nghĩa | Người ký |
|---------|--------|---------|---------|
| **TM.** | Thay mặt | Người đứng đầu ký trực tiếp | Bộ trưởng |
| **KT.** | Ký thay | Cấp phó ký thay người đứng đầu | Thứ trưởng |
| **TL.** | Thừa lệnh | Cấp dưới ký theo ủy quyền | Vụ trưởng |
| **TUQ.** | Thừa ủy quyền | Ký theo ủy quyền chuyển tiếp | Phó Vụ trưởng |

---

## 2. Cách trình bày khối chữ ký

### Bộ trưởng ký trực tiếp (TM.)
```
                              BỘ TRƯỞNG
                          (Ký, ghi rõ họ tên)
                            Nguyễn Văn Thắng
```

### Thứ trưởng ký thay (KT.)
```
                            KT. BỘ TRƯỞNG
                              THỨ TRƯỞNG
                          (Ký, ghi rõ họ tên)
                            Đỗ Thanh Trung
```

### Vụ trưởng ký thừa lệnh (TL.)
```
                            TL. BỘ TRƯỞNG
                      VỤ TRƯỞNG VỤ TỔ CHỨC CÁN BỘ
                          (Ký, ghi rõ họ tên)
                            Nguyễn Văn A
```

### Phó Vụ trưởng ký thừa ủy quyền (TUQ.)
```
                            TL. BỘ TRƯỞNG
                    KT. VỤ TRƯỞNG VỤ TỔ CHỨC CÁN BỘ
                           PHÓ VỤ TRƯỞNG
                          (Ký, ghi rõ họ tên)
                            Trần Văn B
```

---

## 3. Tra cứu: Loại công việc → Cấp ký

| Loại công việc | Cấp ký | Chức vụ |
|---------------|--------|---------|
| Cử đại diện tham gia tổ công tác (Thứ trưởng) | TM. | Bộ trưởng ký |
| Cử đại diện tham gia tổ công tác (cấp Vụ) | KT. | Thứ trưởng ký |
| Văn bản hành chính thông thường | TL. | Vụ trưởng ký |
| Quyết định bổ nhiệm, điều động | TM. | Bộ trưởng ký |
| Quyết định thành lập tổ công tác | TM. | Người đứng đầu cơ quan ký |
| Hướng dẫn nghiệp vụ nội bộ | TL. | Vụ trưởng / Trưởng phòng ký |
| Trả lời kiến nghị, đề nghị | KT. hoặc TL. | Tùy cấp độ vấn đề |

---

## 4. Logic tra cứu tự động cho AI Agent

```
Bước 1: Xác định loại công việc
Bước 2: Xác định cấp độ của người thực hiện (Bộ trưởng / Thứ trưởng / Vụ trưởng)
Bước 3: Áp dụng quy tắc:
  - Người đứng đầu ký trực tiếp → TM.
  - Cấp phó ký thay → KT. + [chức vụ người đứng đầu] + [chức vụ người ký]
  - Cấp dưới ký theo ủy quyền → TL. + [chức vụ người đứng đầu] + [chức vụ người ký]
  - Ủy quyền chuyển tiếp → TUQ. (hiếm, cần xác nhận)
```

---

## 5. Quy tắc trình bày JSON theo từng cap_ky

### cap_ky = "TM"
```json
{
  "cap_ky": "TM",
  "chuc_vu_ky": "BỘ TRƯỞNG",
  "nguoi_ky": "Nguyễn Văn Thắng"
}
```
→ Hiển thị: `BỘ TRƯỞNG` / `(Ký, ghi rõ họ tên)` / `Nguyễn Văn Thắng`

### cap_ky = "KT"
```json
{
  "cap_ky": "KT",
  "chuc_vu_cap_tren": "BỘ TRƯỞNG",
  "chuc_vu_ky": "THỨ TRƯỞNG",
  "nguoi_ky": "Đỗ Thanh Trung"
}
```
→ Hiển thị: `KT. BỘ TRƯỞNG` / `THỨ TRƯỞNG` / `(Ký, ghi rõ họ tên)` / `Đỗ Thanh Trung`

### cap_ky = "TL"
```json
{
  "cap_ky": "TL",
  "chuc_vu_cap_tren": "BỘ TRƯỞNG",
  "chuc_vu_ky": "VỤ TRƯỞNG VỤ TỔ CHỨC CÁN BỘ",
  "nguoi_ky": "Nguyễn Văn A"
}
```
→ Hiển thị: `TL. BỘ TRƯỞNG` / `VỤ TRƯỞNG VỤ TỔ CHỨC CÁN BỘ` / `(Ký, ghi rõ họ tên)` / `Nguyễn Văn A`

---

*Nguồn: Nghị định 30/2020/NĐ-CP, Điều 13 và Phụ lục I*
