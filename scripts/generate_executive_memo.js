const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Footer, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign
} = require('docx');
const fs = require('fs');
const path = require('path');

const DARK_BLUE = "003366";
const DARK_GRAY = "555555";
const WHITE = "FFFFFF";
const PT8 = 16, PT10 = 20, PT14 = 28;
const MARGIN = 1440;
const A4_W = 11906, A4_H = 16838;
const USABLE_W = A4_W - 2 * MARGIN; // 9026

function heading(text) {
  return new Paragraph({
    spacing: { before: 160, after: 60 },
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: DARK_BLUE } },
    children: [new TextRun({ text, bold: true, size: PT10, font: "Calibri", color: DARK_BLUE })]
  });
}

function body(text) {
  return new Paragraph({
    spacing: { before: 0, after: 80, line: 276 },
    children: [new TextRun({ text, size: PT10, font: "Calibri" })]
  });
}

function bullet(text, after = 60) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 0, after, line: 276 },
    children: [new TextRun({ text, size: PT10, font: "Calibri" })]
  });
}

function numbered(ref, text, after = 60) {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 0, after, line: 276 },
    children: [new TextRun({ text, size: PT10, font: "Calibri" })]
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 400, hanging: 400 } } } }]
      },
      {
        reference: "opps",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 400, hanging: 400 } } } }]
      },
      {
        reference: "actions",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 400, hanging: 400 } } } }]
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: A4_W, height: A4_H },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "CONFIDENTIAL \u2014 For internal executive use only", size: PT8, italics: true, color: DARK_GRAY, font: "Calibri" })]
        })]
      })
    },
    children: [
      // ── Header bar ──────────────────────────────────────────────────────────
      new Table({
        columnWidths: [USABLE_W],
        width: { size: USABLE_W, type: WidthType.DXA },
        rows: [new TableRow({
          children: [new TableCell({
            width: { size: USABLE_W, type: WidthType.DXA },
            shading: { fill: DARK_BLUE, type: ShadingType.CLEAR },
            margins: { top: 160, bottom: 160, left: 240, right: 240 },
            verticalAlign: VerticalAlign.CENTER,
            borders: {
              top: { style: BorderStyle.NONE, size: 0, color: "auto" },
              bottom: { style: BorderStyle.NONE, size: 0, color: "auto" },
              left: { style: BorderStyle.NONE, size: 0, color: "auto" },
              right: { style: BorderStyle.NONE, size: 0, color: "auto" }
            },
            children: [new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "EXECUTIVE BRIEFING: Vendor Portfolio Review \u2014 Cost Reduction Opportunities", bold: true, size: PT14, font: "Calibri", color: WHITE })]
            })]
          })]
        })]
      }),

      // ── Sub-header ───────────────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 80, after: 100 },
        children: [new TextRun({ text: "Date: March 31, 2026  |  Prepared for: CEO & CFO  |  Prepared by: VP of Operations", size: PT10, font: "Calibri", color: DARK_GRAY })]
      }),

      // ── BOTTOM LINE ──────────────────────────────────────────────────────────
      heading("BOTTOM LINE"),
      body("A 386-vendor, $7.9M annual spend audit has identified $905,000 in near-term, actionable savings across three initiatives. Salesforce UK Ltd \u2014 at $3.1M or 39.5% of total vendor spend \u2014 is the single highest-priority renegotiation target. CFO approval is required to begin formal vendor exit and renegotiation conversations by April 2026."),

      // ── KEY FINDINGS ─────────────────────────────────────────────────────────
      heading("KEY FINDINGS"),
      bullet("Spend concentration: Salesforce UK Ltd ($3.1M) accounts for 39.5% of total annual vendor spend, creating both significant negotiation leverage and single-vendor dependency risk."),
      bullet("Facilities fragmentation: 122 vendors across $1.2M \u2014 under $10K per vendor average \u2014 including two overlapping Zagreb office leases totaling $328K (Zagrebtower + Weking D.O.O.)."),
      bullet("Tail vendor overload: 203 of 386 vendors (53%) are recommended for termination; the majority are sub-$5K annual lines that can be cut with minimal operational impact."),
      bullet("Finance duplication: BDO LLP, Grant Thornton, and Harmonic Group provide overlapping audit/advisory functions; Sage UK and Planful both serve FP&A planning needs.", 80),

      // ── TOP 3 SAVINGS OPPORTUNITIES ──────────────────────────────────────────
      heading("TOP 3 SAVINGS OPPORTUNITIES"),
      numbered("opps", "Salesforce License Audit & Renegotiation \u2014 Est. $500,000 \u2014 Seat utilization audit and 15% contract reduction leveraged against Dynamics/HubSpot competition; consolidate HubSpot Ireland ($32K) into Salesforce native marketing automation."),
      numbered("opps", "Croatia & Global Facilities Consolidation \u2014 Est. $245,000 \u2014 Exit Weking D.O.O. Zagreb lease ($144K), terminate 40+ sub-$5K Croatian tail vendors (~$60K combined), and consolidate overlapping real estate advisors (JLL/CBRE)."),
      numbered("opps", "Finance & Audit Advisory Rationalization \u2014 Est. $160,000 \u2014 Terminate Grant Thornton ($46K) and Harmonic Group ($65K); migrate off Sage UK ($47K) to Planful; exit Cedar Recruitment ($19K).", 80),

      // ── IMPLEMENTATION TIMELINE ──────────────────────────────────────────────
      heading("IMPLEMENTATION TIMELINE"),
      bullet("Month 1\u20132: Terminate 200+ sub-threshold vendors; initiate Salesforce seat utilization audit; serve legal notice on Weking D.O.O. Zagreb lease."),
      bullet("Month 3\u20134: Begin Salesforce contract renegotiation at renewal; wind down Grant Thornton and Harmonic Group engagements; consolidate Croatian vendor tail."),
      bullet("Month 5\u20136: Complete Sage UK to Planful migration; finalize Zagreb real estate consolidation; exit Cedar Recruitment."),
      bullet("Month 6+: Full $905K annualized savings realized; implement vendor governance policy to prevent tail re-growth.", 80),

      // ── RECOMMENDED ACTIONS ──────────────────────────────────────────────────
      heading("RECOMMENDED ACTIONS"),
      numbered("actions", "Authorize vendor termination list (203 vendors) \u2014 Owner: VP Operations \u2014 April 2026"),
      numbered("actions", "Initiate Salesforce seat audit and renegotiation mandate \u2014 Owner: CFO / Finance \u2014 April 2026"),
      numbered("actions", "Issue notice on Weking D.O.O. Zagreb lease per contract terms \u2014 Owner: Procurement \u2014 April 2026", 80),

      // ── RISKS & CONSIDERATIONS ───────────────────────────────────────────────
      heading("RISKS & CONSIDERATIONS"),
      bullet("Salesforce dependency: At $3.1M and 40% of total spend, renegotiation must protect service continuity; a parallel competitive evaluation (Dynamics, HubSpot) strengthens leverage without committing to migration."),
      bullet("Contractual lock-in on facility leases: Zagreb exit is subject to local notice periods and early termination fees \u2014 legal review required before serving notice; net Year 1 savings may be lower than projected."),
      bullet("Transition costs: Finance system migration (Sage to Planful) and advisory firm transitions carry one-time switching costs (~$15\u201325K), excluded from the $905K savings figure.", 100),

      // ── Footer note (in-body) ─────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 80, after: 0 },
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: DARK_GRAY } },
        children: [
          new TextRun({ text: "Auto Generated by AI with Confidence: HIGH  |  Source: Internal vendor spend data (12-month)  |  Reviewer: VP of Operations", size: PT8, italics: true, color: DARK_GRAY, font: "Calibri" })
        ]
      })
    ]
  }]
});

const outPath = path.resolve(__dirname, '..', 'outputs', 'Executive Memo.docx');
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log('Done:', outPath);
});
