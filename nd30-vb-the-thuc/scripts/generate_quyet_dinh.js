/**
 * generate_quyet_dinh.js
 * Sinh file .docx Quyết định hành chính đúng thể thức Nghị định 30/2020/NĐ-CP
 * Tác giả: Leo | Cập nhật: 26/03/2026
 *
 * Sử dụng:
 *   node generate_quyet_dinh.js --input data.json --output quyet_dinh.docx
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, LineRuleType, VerticalAlign,
} = require("docx");
const fs = require("fs");

// ─── Parse arguments ────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const inputIdx = args.indexOf("--input");
const outputIdx = args.indexOf("--output");
if (inputIdx === -1 || outputIdx === -1) {
  console.error("Sử dụng: node generate_quyet_dinh.js --input data.json --output quyet_dinh.docx");
  process.exit(1);
}
const data = JSON.parse(fs.readFileSync(args[inputIdx + 1], "utf8"));
const outputFile = args[outputIdx + 1];

// ─── Hằng số thể thức ────────────────────────────────────────────────────────
const FONT = "Times New Roman";
const COL_LEFT = 3500;
const COL_RIGHT = 5571;
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

const noBorder = {
  top: { style: BorderStyle.NONE, size: 0 }, bottom: { style: BorderStyle.NONE, size: 0 },
  left: { style: BorderStyle.NONE, size: 0 }, right: { style: BorderStyle.NONE, size: 0 },
};

// ─── Ngày tháng ──────────────────────────────────────────────────────────────
const now = new Date();
const ngay = data.ngay || `ngày ${now.getDate()} tháng ${now.getMonth() + 1} năm ${now.getFullYear()}`;
const diadanh = data.dia_danh || "Hà Nội";
const soKyHieu = data.so_ky_hieu || `    /${data.don_vi_soan_thao || "QĐ"}`;

// ─── Header Table (giống công văn) ───────────────────────────────────────────
const headerTable = new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  borders: { top: noBorder.top, bottom: noBorder.bottom, left: noBorder.left, right: noBorder.right, insideH: noBorder.top, insideV: noBorder.left },
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: COL_LEFT, type: WidthType.DXA },
          borders: noBorder,
          verticalAlign: VerticalAlign.TOP,
          children: [
            para(txt(data.co_quan_chu_quan || "", { size: 13, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 60, line: 300, lineRule: LineRuleType.EXACT } }),
            para(txt(data.co_quan_ban_hanh || "", { size: 13, bold: true, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
            new Paragraph({ spacing: { before: 20, after: 0 }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, indent: { left: 1350, right: 1350 }, children: [] }),
          ],
        }),
        new TableCell({
          width: { size: COL_RIGHT, type: WidthType.DXA },
          borders: noBorder,
          verticalAlign: VerticalAlign.TOP,
          children: [
            para(txt("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", { size: 13, bold: true, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 60, line: 300, lineRule: LineRuleType.EXACT } }),
            para(txt("Độc lập - Tự do - Hạnh phúc", { size: 14, bold: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
            new Paragraph({ spacing: { before: 20, after: 0 }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, indent: { left: 1100, right: 1100 }, children: [] }),
          ],
        }),
      ],
    }),
    new TableRow({
      children: [
        new TableCell({
          width: { size: COL_LEFT, type: WidthType.DXA },
          borders: noBorder,
          children: [
            para(txt(`Số: ${soKyHieu}`, { size: 13 }), { align: AlignmentType.LEFT, spacing: { before: 120, after: 0, line: 300, lineRule: LineRuleType.EXACT } }),
          ],
        }),
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

// ─── Tên loại + Trích yếu ────────────────────────────────────────────────────
const tenLoaiBlock = [
  para(txt(""), { spacing: { before: 240, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
  para(txt("QUYẾT ĐỊNH", { size: 14, bold: true, caps: true }), { align: AlignmentType.CENTER, spacing: { before: 0, after: 0, line: 340, lineRule: LineRuleType.EXACT } }),
  para(txt(data.trich_yeu || "", { size: 14, bold: true }), { align: AlignmentType.CENTER, spacing: { before: 60, after: 0, line: 340, lineRule: LineRuleType.EXACT } }),
  // Gạch ngang dưới trích yếu
  new Paragraph({ spacing: { before: 20, after: 120 }, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "000000", space: 1 }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, indent: { left: 2000, right: 2000 }, children: [] }),
];

// ─── Căn cứ ──────────────────────────────────────────────────────────────────
const canCuList = data.can_cu || [];
const canCuParagraphs = canCuList.map((cc, idx) => {
  const isLast = idx === canCuList.length - 1;
  return para(txt(`Căn cứ ${cc}${isLast ? "," : ";"}`, { size: 14, italic: true }), { align: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 60, line: 340, lineRule: LineRuleType.EXACT } });
});

// ─── Nội dung (theo Điều) ────────────────────────────────────────────────────
const noiDungRaw = data.noi_dung || "";
let noiDungParagraphs = [];

if (Array.isArray(noiDungRaw)) {
  // Mảng các Điều
  noiDungRaw.forEach(dieu => {
    if (dieu.tieu_de) {
      noiDungParagraphs.push(para(txt(dieu.tieu_de, { size: 14, bold: true }), { align: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, spacing: LINE_SPACING }));
    }
    if (dieu.noi_dung) {
      dieu.noi_dung.split("\n").filter(Boolean).forEach(line => {
        noiDungParagraphs.push(para(txt(line, { size: 14 }), { align: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, spacing: LINE_SPACING }));
      });
    }
  });
} else {
  // Chuỗi văn bản, tự phát hiện "Điều X."
  noiDungRaw.split("\n").filter(Boolean).forEach(line => {
    const isArticle = /^Điều\s+\d+\./.test(line.trim());
    noiDungParagraphs.push(para(txt(line, { size: 14, bold: isArticle }), { align: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, spacing: LINE_SPACING }));
  });
}

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
for (let i = 0; i < 3; i++) chuKyLines.push(para(txt(""), { spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));
chuKyLines.push(para(txt(nguoiKy, { size: 14, bold: true }), { align: AlignmentType.RIGHT, spacing: { before: 0, after: 0, line: 300, lineRule: LineRuleType.EXACT } }));

// ─── Nơi nhận ─────────────────────────────────────────────────────────────────
const noiNhan = data.noi_nhan || ["- Như Điều 3;", "- Lưu: VT."];
const noiNhanParagraphs = [
  para([txt("Nơi nhận:", { size: 12, bold: true, italic: true })], { spacing: { before: 240, after: 0, line: 280, lineRule: LineRuleType.EXACT } }),
  ...noiNhan.map(nn => para(txt(nn, { size: 11 }), { spacing: { before: 0, after: 0, line: 280, lineRule: LineRuleType.EXACT } })),
];

// ─── Tạo Document ─────────────────────────────────────────────────────────────
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: MARGIN_TOP, right: MARGIN_RIGHT, bottom: MARGIN_BOTTOM, left: MARGIN_LEFT },
      },
    },
    children: [
      headerTable,
      ...tenLoaiBlock,
      ...canCuParagraphs,
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
