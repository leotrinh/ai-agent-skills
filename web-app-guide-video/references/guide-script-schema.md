# guide.json schema

```jsonc
{
  "url": "https://app.example.com/",      // or "prototype/index.html" (local path)
  "voice": "vi-VN-HoaiMyNeural",
  "rate": "+5%",                           // edge-tts speed
  "viewport": [1600, 900],                 // optional
  "output": "data-marketing-guide.mp4",    // optional, default <json name>.mp4
  "steps": [ /* Step, in playback order */ ]
}
```

## Step

| Field | Type | Meaning |
|---|---|---|
| `say` | string | Narration (also becomes subtitles, split per sentence) |
| `label` | string | Pill left part, e.g. `BƯỚC 3`, `STEP 3`, `GIỚI THIỆU`. Empty → no label |
| `title` | string | Pill right part, usually the feature name |
| `badge` | string | Number on the frame corner (`"3"`, `"7.2"`); empty → none |
| `actions` | Action[] | Run before overlay is drawn; empty for intro on current screen |
| `target` | object/null | Element to spotlight; `null` → pill only |
| `blur` | `true` / string[] | `true` = blur `table tbody`; list = CSS selectors to blur |

**Target** — one of:
- `{"css": "table"}` — first match.
- `{"text": "RECOMMENDED ORDER", "minW": 900}` — element containing text, climbing parents until width ≥ `minW` px (frames a whole card/section instead of one label).

**Action** — exactly one key per object:
- `{"click": "Leads"}` — visible element with exact text (sidebar items, tabs).
- `{"click": {"css": "#menu-toggle"}}` / `{"click": {"text": "Campaigns", "within": "nav .subnav"}}` — disambiguate duplicates.
- `{"hover": "Reports"}`, `{"scroll": 600}`, `{"wait": 1000}`
- `{"goto": "/settings"}` (relative to `url`) or full URL.
- `{"type": {"css": "input[name=q]", "value": "demo"}}` — prototypes/test only.

## Example (excerpt of a real CRM tour)

```json
{
  "url": "https://crm.example.com/",
  "voice": "vi-VN-HoaiMyNeural",
  "rate": "+5%",
  "output": "crm-data-marketing.mp4",
  "steps": [
    {"label": "GIỚI THIỆU", "title": "Data & Marketing", "target": {"css": "nav .subnav"},
     "say": "Chào mừng bạn đến với CRM. Trong video này, chúng ta sẽ tìm hiểu các chức năng trong mục Data và Marketing."},
    {"label": "BƯỚC 1", "title": "Contacts", "badge": "1", "actions": [{"click": "Contacts"}],
     "target": {"css": "table"}, "blur": true,
     "say": "Contacts là danh bạ trung tâm của những người được thu thập từ form, sự kiện và chiến dịch."},
    {"label": "BƯỚC 2", "title": "Email Campaigns", "badge": "2.1",
     "actions": [{"click": "Email Marketing"}, {"click": {"text": "Campaigns", "within": "nav"}}],
     "target": {"text": "Select an exact lead audience", "minW": 900},
     "say": "Mục Campaigns cho phép tạo chiến dịch email cho đúng tập lead đã chọn và lên lịch gửi hàng loạt."},
    {"label": "KẾT THÚC", "title": "Cảm ơn bạn đã theo dõi", "actions": [{"click": "Dashboard"}], "target": null,
     "say": "Đó là toàn bộ các chức năng trong mục Data và Marketing. Cảm ơn bạn đã theo dõi."}
  ]
}
```

Writing tips: ~10–15 s per step; explain purpose and when to use it; keep English UI names as-is so viewers can find them; intro + outro steps make the video feel finished.
