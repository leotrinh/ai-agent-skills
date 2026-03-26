/**
 * generate_cong_van.js
 * Sinh file .docx Công văn đúng thể thức Nghị định 30/2020/NĐ-CP
 * Tác giả: Leo | Cập nhật: 26/03/2026
 *
 * Sử dụng:
 *   node generate_cong_van.js --input data.json --output cong_van.docx
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, LineRuleType,
  ShadingType, VerticalAlign, HeadingLevel,
} = require("docx");
const fs = require("fs");
const path = require("path");

// ─── Parse arguments ────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const inputIdx = args.indexOf("--input");
const outputIdx = args.indexOf("--output");
if (inputIdx === -1 || outputIdx === -1) {
  console.error("Sử dụng: node generate_cong_van.js --input data.json --output cong_van.docx");
  process.exit(1);
}
const inputFile = args[inputIdx + 1];
const outputFile = args[outputIdx + 1];
const data = JSON.parse(fs.readFileSync(inputFile, "utf8"));

// ─── Hằng số thể thức ────────────────────────────────────────────────────────
const FONT = "Times New Roman";
const COL_LEFT = 3500;   // dxa
const COL_RIGHT = 5571;  // dxa
const MARGIN_LEFT = 1701;
const MARGIN_RIGHT = 1134;
const MARGIN_TOP = 1134;
const MARGIN_BOTTOM = 1134;
const LINE_SPACING = { before: 120, after: 120, line: 340, lineRule: LineRuleType.EXACT };

// ─── Helpers ─────────────────────────────────────────────────────────────────
const txt = (text, opts = {}) => new TextRun({
  text, font: FONT, size: (opts.size || 14) * 2,
  bold: opts.bold || false, italics: opts.italic || false,
  allCaps: opts.caps || false,
});

const para = (runs, opts = {}) => new Paragraph({
  children: Array.isArray(runs) ? runs : [runs],
  alignment: opts.align || AlignmentType.LEFT,
  spacing: opts.spacing || LINE_SPACING,
  indent: opts.indent || {},
  border: opts.border || {},
});

const noBorder = { top: { style: BorderStyle.NONE, size: 0 }, bottom: { style: BorderStyle.NONE, size: 0 }, left: { style: BorderStyle.NONE, size: 0 }, right: { style: BorderStyle.NONE, size: 0 } };
const borderTop = { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE, size: 0 }, left: { style: BorderStyle.NONE, size: 0 }, right: { style: BorderStyle.NONE, size: 0 } };

// ─── Ngày tháng ──────────────────────────────────────────────────────────────
const now = new Date();
const ngay = data.ngay || `ngày ${now.getDate()} tháng ${now.getMonth() + 1} năm ${now.getFullYear()}`;
const diadanh = data.dia_danh || "Hà Nội";

// ─── Số ký hiệu ──────────────────────────────────────────────────────────────
const soKyHieu = data.so_ky_hieu || `    /${data.don_vi_soan_thao || "CV"}`;

// ─── Header Table ────────────────────────────────────────────────────────────
const headerTable = new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  borders: { top: noBorder.top, bottom: noBorder.bottom, left: noBorder.left, right: noBorder.right, insideH: noBorder.top, insideV: noBorder.left },
  rows: [
    // Dòng 1
    new TableRow({
      children: [
        // Cột trái: Cơ quan chủ quản + Cơ quan ban hành
        new TableCell({
          width: { size: COL_LEFT, type: WidthType.DXA },
          borders: noBorder,
          verticalAlign: VerticalAlign.TOP,
          children: [
            para(txt(data.co_quan_chu_quan || "", { size: 13, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 60, line: 300, lineRule: LineRuleType.EXACT } }),
            para(txt(data.co_quan_ban_hanh || "", { size: 13, bold: true, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
            // Gạch ngang dưới tên cơ quan ban hành
            new Paragraph({ spacing: { before: 20, after: 0 }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, indent: { left: 1350, right: 1350 }, children: [] }),
          ],
        }),
        // Cột phải: Quốc hiệu + Tiêu ngữ
        new TableCell({
          width: { size: COL_RIGHT, type: WidthType.DXA },
          borders: noBorder,
          verticalAlign: VerticalAlign.TOP,
          children: [
            para(txt("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", { size: 13, bold: true, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 60, line: 300, lineRule: LineRuleType.EXACT } }),
            para(txt("Độc lập - Tự do - Hạnh phúc", { size: 14, bold: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
            // Gạch ngang dưới tiêu ngữ
            new Paragraph({ spacing: { before: 20, after: 0 }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, indent: { left: 1100, right: 1100 }, children: [] }),
          ],
        }),
      ],
    }),
    // Dòng 2
    new TableRow({
      children: [
        // Cột trái: Số ký hiệu + Trích yếu
        new TableCell({
          width: { size: COL_LEFT, type: WidthType.DXA },
          borders: noBorder,
          children: [
            para(txt(`Số: ${soKyHieu}`, { size: 13 }), { align: AlignmentType.LEFT, spacing: { before: 120, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
            para(txt(data.trich_yeu || "", { size: 12 }), { align: AlignmentType.LEFT, spacing: { before: 0, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
          ],
        }),
        // Cột phải: Địa danh, ngày tháng
        new TableCell({
          width: { size: COL_RIGHT, type: WidthType.DXA },
          borders: noBorder,
          children: [
            para(txt(`${diadanh}, ${ngay}`, { size: 14, italic: true }), { align: AlignmentType.CENTER, spacing: { before: 120, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
          ],
        }),
      ],
    }),
  ],
});

// ─── Kính gửi ─────────────────────────────────────────────────────────────────
const kinhGuiParagraphs = [];
const kinhGui = data.kinh_gui || [];
if (kinhGui.length === 1) {
  kinhGuiParagraphs.push(para([txt("Kính gửi: ", { size: 14, bold: true }), txt(kinhGui[0], { size: 14 })], { spacing: LINE_SPACING }));
} else {
  kinhGuiParagraphs.push(para(txt("Kính gửi:", { size: 14, bold: true }), { spacing: { before: 120, after: 0, line: 340, lineRule: LineRuleType.EXACT } }));
  kinhGui.forEach(kg => {
    kinhGuiParagraphs.push(para(txt(`- ${kg}`, { size: 14 }), { indent: { left: 720 }, spacing: { before: 0, after: 0, line: 340, lineRule: LineRuleType.EXACT } }));
  });
}

// ─── Nội dung ─────────────────────────────────────────────────────────────────
const noiDungParagraphs = (data.noi_dung || "").split("\n").filter(Boolean).map(line =>
  para(txt(line, { size: 14 }), { align: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, spacing: LINE_SPACING })
);

// ─── Khối chữ ký ──────────────────────────────────────────────────────────────
const capKy = (data.cap_ky || "TM").toUpperCase();
const chucVuCapTren = data.chuc_vu_cap_tren || "";
const chucVuKy = data.chuc_vu_ky || "";
const nguoiKy = data.nguoi_ky || "";

const chuKyLines = [];
if (capKy === "TM") {
  chuKyLines.push(para(txt(chucVuKy, { size: 13, bold: true, caps: true }), { align: AlignmentType.RIGHT, spacing: { before: 240, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
} else {
  chuKyLines.push(para(txt(`${capKy}. ${chucVuCapTren}`, { size: 13, bold: true, caps: true }), { align: AlignmentType.RIGHT, spacing: { before: 240, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
  chuKyLines.push(para(txt(chucVuKy, { size: 13, bold: true, caps: true }), { align: AlignmentType.RIGHT, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
}
chuKyLines.push(para(txt("(Ký, ghi rõ họ tên)", { size: 14, italic: true }), { align: AlignmentType.RIGHT, spacing: { before: 60, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
// 3 dòng trống cho chữ ký
for (let i = 0; i < 3; i++) chuKyLines.push(para(txt(""), { spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
chuKyLines.push(para(txt(nguoiKy, { size: 14, bold: true }), { align: AlignmentType.RIGHT, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));

// ─── Nơi nhận ─────────────────────────────────────────────────────────────────
const noiNhan = data.noi_nhan || ["- Như trên;", "- Lưu: VT."];
const noiNhanParagraphs = [
  para([txt("Nơi nhận:", { size: 12, bold: true, italic: true })], { spacing: { before: 240, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
  ...noiNhan.map(nn => para(txt(nn, { size: 11 }), { spacing: { before: 0, after: 0, line: 280, lineRule: LineRuleType.EXACT } })),
];

// ─── Tạo Document ─────────────────────────────────────────────────────────────
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4 in twips
        margin: { top: MARGIN_TOP, right: MARGIN_RIGHT, bottom: MARGIN_BOTTOM, left: MARGIN_LEFT },
      },
    },
    children: [
      headerTable,
      para(txt(""), { spacing: { before: 120, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
      ...kinhGuiParagraphs,
      para(txt(""), { spacing: { before: 60, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
      ...noiDungParagraphs,
      ...chuKyLines,
      ...noiNhanParagraphs,
    ],
  }],
});

// ─── Xuất file ────────────────────────────────────────────────────────────────
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputFile, buffer);
  console.log(`✅ Đã tạo: ${outputFile}`);
}).catch(err => {
  console.error("❌ Lỗi:", err.message);
  process.exit(1);
});
