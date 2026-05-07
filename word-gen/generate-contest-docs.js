/**
 * 融媒技术创新大赛申报材料 - Word文档生成脚本
 * 严格遵守党政机关公文格式（GB/T 9704-2012）
 */

const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, convertInchesToTwip,
  TableLayoutType, VerticalAlign, ShadingType, ImageRun
} = require('docx');
const fs = require('fs');
const path = require('path');

const SKILL_ROOT = '/home/lytv/.claude/skills/rm-contest-writer';
const FONTS_DIR = path.join(SKILL_ROOT, 'fonts');

const FORMAT = {
  // GB/T 9704-2012: A4, 上37mm 下35mm 左28mm 右26mm
  pageMargin: {
    top: 2098,    // 37mm × 56.7twip/mm
    bottom: 1985,  // 35mm × 56.7twip/mm
    left: 1588,    // 28mm × 56.7twip/mm
    right: 1474,   // 26mm × 56.7twip/mm
  },
  fontSize: {
    title: 44,       // 2号 = 22pt = 44 half-points（方正小标宋）
    heading1: 32,    // 3号 = 16pt = 32 half-points（黑体）
    heading2: 32,    // 3号 = 16pt = 32 half-points（楷体）
    heading3: 32,    // 3号 = 16pt = 32 half-points（仿宋）
    body: 32,        // 3号 = 16pt = 32 half-points（仿宋）
    small: 28,        // 小五号
  },
  // 28.9pt 固定行距 = 578 twip (28.9 × 20)
  lineSpacing: 578,
  lineRule: 'exact',
  // 首行缩进2字 = 2 × 28pt(仿宋3号半宽) ≈ 56twip（取整）
  firstLineIndent: 567,  // 首行左空二字符：仿宋3号(16pt)每字≈5.37mm，2字≈10.74mm≈567twip
};

function readMarkdownFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    console.error(`无法读取文件: ${filePath}`);
    return '';
  }
}

function parseInlineFormats(text) {
  const segments = [];
  let remaining = text;
  const boldRegex = /\*\*([^*]+)\*\*/;

  while (remaining) {
    const match = remaining.match(boldRegex);
    if (match) {
      const before = remaining.substring(0, match.index);
      if (before) segments.push({ text: before, bold: false });
      segments.push({ text: match[1], bold: true });
      remaining = remaining.substring(match.index + match[0].length);
    } else {
      segments.push({ text: remaining, bold: false });
      break;
    }
  }
  return segments;
}

function parseMarkdownTable(lines, startIdx) {
  const tableLines = [];
  let idx = startIdx;

  while (idx < lines.length) {
    const line = lines[idx];
    if (line.trim().startsWith('|')) {
      tableLines.push(line);
      idx++;
    } else {
      break;
    }
  }

  if (tableLines.length < 2) return null;

  const rows = [];
  for (const tableLine of tableLines) {
    if (/^\|[\s\-:|]+\|$/.test(tableLine.trim())) continue;
    const cells = tableLine.split('|').filter((c, i, arr) => i > 0 && i < arr.length - 1);
    const cleanCells = cells.map(cell => {
      return cell.trim().replace(/<[^>]+>/g, '').replace(/&nbsp;/g, '');
    });
    rows.push(cleanCells);
  }

  if (rows.length === 0) return null;
  return { rows, endIdx: idx };
}

function createTable(rows) {
  if (rows.length === 0) return null;

  const headerRow = rows[0];
  const dataRows = rows.slice(1);

  const createCell = (text, isHeader) => new TableCell({
    children: [new Paragraph({
      children: [new TextRun({
        text: text || '',
        font: { name: isHeader ? '方正小标宋简体' : '仿宋_GB2312' },
        size: isHeader ? 24 : 21,
        bold: isHeader,
      })],
      alignment: AlignmentType.CENTER,
      spacing: { line: FORMAT.lineSpacing, lineRule: 'exact' },
    })],
    verticalAlign: VerticalAlign.CENTER,
    shading: isHeader ? { type: ShadingType.CLEAR, fill: 'E8E8E8' } : undefined,
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
      new TableRow({ children: headerRow.map(c => createCell(c, true)), tableHeader: true }),
      ...dataRows.map(row => new TableRow({ children: row.map(c => createCell(c || '', false)) }))
    ],
    layout: TableLayoutType.FIXED,
  });
}

function parseMarkdownToParagraphs(markdown) {
  const lines = markdown.split('\n');
  const paragraphs = [];
  let currentParagraph = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const trimmedLine = line.trim();

    if (trimmedLine.includes('&nbsp;') && !currentParagraph.length && !trimmedLine.startsWith('|') && !trimmedLine.startsWith('-')) {
      i++;
      continue;
    }

    if (trimmedLine === '') {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      i++;
      continue;
    }

    if (/^---+$/.test(trimmedLine)) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      i++;
      continue;
    }

    if (trimmedLine.startsWith('|')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      const tableResult = parseMarkdownTable(lines, i);
      if (tableResult) {
        paragraphs.push({ text: tableResult.rows, style: 'table' });
        i = tableResult.endIdx;
        continue;
      }
    }

    if (trimmedLine.startsWith('# ')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      const titleText = trimmedLine.substring(2).replace(/\*\*([^*]+)\*\*/g, '$1');
      paragraphs.push({ text: titleText, style: '作品名称' });
      i++;
      continue;
    }
    if (trimmedLine.startsWith('## ')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      const h1Text = trimmedLine.substring(3).replace(/\*\*([^*]+)\*\*/g, '$1');
      paragraphs.push({ text: h1Text, style: '一级标题' });
      i++;
      continue;
    }
    if (trimmedLine.startsWith('### ')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      const h2Text = trimmedLine.substring(4).replace(/\*\*([^*]+)\*\*/g, '$1');
      paragraphs.push({ text: h2Text, style: '二级标题' });
      i++;
      continue;
    }

    if (/^[一二三四五六七八九十]、/.test(trimmedLine)) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine, style: '一级标题' });
      i++;
      continue;
    }
    if (/^\(\d+\)/.test(trimmedLine)) {
      // 四级标题：阿拉伯数字括号，如"（4）"，需在二级标题之前匹配
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine, style: '四级标题' });
      i++;
      continue;
    }
    if (/^\([^一二三四五六七八九十]\)/.test(trimmedLine)) {
      // 二级标题：中文数字括号，如"（二）"
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine, style: '二级标题' });
      i++;
      continue;
    }
    if (/^\d+\./.test(trimmedLine)) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine, style: '三级标题' });
      i++;
      continue;
    }

    if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine.substring(2), style: '列表', firstLineIndent: 567 });
      i++;
      continue;
    }

    if (trimmedLine.startsWith('> ')) {
      if (currentParagraph.length > 0) {
        paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
        currentParagraph = [];
      }
      paragraphs.push({ text: trimmedLine.substring(2), style: '说明' });
      i++;
      continue;
    }

    const cleanLine = line.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, '');
    if (cleanLine.trim()) {
      currentParagraph.push(cleanLine);
    }
    i++;
  }

  if (currentParagraph.length > 0) {
    paragraphs.push({ text: currentParagraph.join(''), style: 'body' });
  }

  return paragraphs;
}

function createBodyParagraph(text, indent = FORMAT.firstLineIndent) {
  const segments = parseInlineFormats(text);
  const runs = segments.map(seg => new TextRun({
    text: seg.text,
    font: { name: '仿宋_GB2312' },
    size: FORMAT.fontSize.body,
    bold: seg.bold,
  }));

  return new Paragraph({
    children: runs,
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: indent },
    spacing: { line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createTitleParagraph(text) {
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '方正小标宋简体' },
      size: FORMAT.fontSize.title,
      bold: true,
    })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 200, line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createHeading1Paragraph(text) {
  // 一级标题：黑体3号，"一、"格式，居左
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '黑体' },
      size: FORMAT.fontSize.heading1,
      bold: true,
    })],
    alignment: AlignmentType.LEFT,
    spacing: { before: 200, after: 100, line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createHeading2Paragraph(text) {
  // 二级标题：楷体GB2312 3号，"（二）"格式
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '楷体_GB2312' },
      size: FORMAT.fontSize.heading2,
      bold: true,
    })],
    alignment: AlignmentType.LEFT,
    spacing: { before: 150, after: 80, line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createHeading3Paragraph(text) {
  // 三级标题：仿宋GB2312 3号，"3."格式
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '仿宋_GB2312' },
      size: FORMAT.fontSize.heading3,
      bold: false,
    })],
    alignment: AlignmentType.LEFT,
    spacing: { before: 120, after: 60, line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createHeading4Paragraph(text) {
  // 四级标题：仿宋GB2312 3号，"（4）"格式
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '仿宋_GB2312' },
      size: FORMAT.fontSize.heading3,
      bold: false,
    })],
    alignment: AlignmentType.LEFT,
    spacing: { before: 100, after: 50, line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createBulletParagraph(text, indent = 567) {
  const segments = parseInlineFormats(text);
  const runs = segments.map(seg => new TextRun({
    text: seg.text,
    font: { name: '仿宋_GB2312' },
    size: FORMAT.fontSize.body,
    bold: seg.bold,
  }));

  return new Paragraph({
    children: runs,
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: indent },
    spacing: { line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createSignatureParagraph(text) {
  return new Paragraph({
    children: [new TextRun({
      text: text,
      font: { name: '仿宋_GB2312' },
      size: FORMAT.fontSize.body,
    })],
    alignment: AlignmentType.RIGHT,
    indent: { right: convertInchesToTwip(0.167) },
    spacing: { line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function createEmptyParagraph() {
  return new Paragraph({
    children: [new TextRun({ text: '', font: { name: '仿宋_GB2312' }, size: FORMAT.fontSize.body })],
    spacing: { line: FORMAT.lineSpacing, lineRule: 'exact' },
  });
}

function isSignatureLine(text) {
  return text.includes('团队/个人：') ||
         text.includes('（公章）') ||
         (text.includes('年') && text.includes('月') && text.includes('日') && text.length < 20) ||
         text.includes('甲方（公章）：') ||
         text.includes('乙方（公章）：');
}

async function generateDoc(markdownPath, outputPath, imagePaths = []) {
  console.log(`生成文档: ${markdownPath}`);

  const content = readMarkdownFile(markdownPath);
  if (!content) {
    console.error(`  文件不存在: ${markdownPath}`);
    return false;
  }

  const parsedParagraphs = parseMarkdownToParagraphs(content);
  const docParagraphs = [];

  for (const p of parsedParagraphs) {
    if (p.style === 'table') {
      const table = createTable(p.text);
      if (table) {
        docParagraphs.push(table);
        docParagraphs.push(createEmptyParagraph());
      }
      continue;
    }

    if (isSignatureLine(p.text)) {
      docParagraphs.push(createSignatureParagraph(p.text));
    } else {
      switch (p.style) {
        case '作品名称':
          docParagraphs.push(createTitleParagraph(p.text));
          break;
        case '一级标题':
          docParagraphs.push(createHeading1Paragraph(p.text));
          break;
        case '二级标题':
          docParagraphs.push(createHeading2Paragraph(p.text));
          break;
        case '三级标题':
          docParagraphs.push(createHeading3Paragraph(p.text));
          break;
        case '四级标题':
          docParagraphs.push(createHeading4Paragraph(p.text));
          break;
        case '列表':
          docParagraphs.push(createBulletParagraph(p.text, p.firstLineIndent || 567));
          break;
        case '说明':
          docParagraphs.push(createBulletParagraph(p.text, 567));
          break;
        default:
          if (p.text.trim()) {
            docParagraphs.push(createBodyParagraph(p.text));
          }
      }
    }
  }

  if (imagePaths && imagePaths.length > 0) {
    for (const imgPath of imagePaths) {
      if (fs.existsSync(imgPath)) {
        const imageBuffer = fs.readFileSync(imgPath);
        docParagraphs.push(createEmptyParagraph());
        docParagraphs.push(new Paragraph({
          children: [
            new ImageRun({
              data: imageBuffer,
              transformation: { width: 600, height: 400 },
              type: 'png',
            }),
          ],
          alignment: AlignmentType.CENTER,
        }));
        docParagraphs.push(createEmptyParagraph());
      }
    }
  }

  const doc = new Document({
    sections: [{
      properties: { page: { margin: FORMAT.pageMargin } },
      children: docParagraphs,
    }],
  });

  try {
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputPath, buffer);
    console.log(`  成功: ${outputPath}`);
    return true;
  } catch (e) {
    console.error(`  失败: ${e.message}`);
    return false;
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log('用法: node generate-contest-docs.js <markdown文件> <输出docx文件> [架构图1.png] [架构图2.png] ...');
    process.exit(1);
  }

  const markdownPath = args[0];
  const outputPath = args[1];
  const imagePaths = args.slice(2);

  console.log('='.repeat(60));
  console.log('融媒技术创新大赛申报材料 - Word文档生成');
  console.log('='.repeat(60));
  console.log('');
  console.log('公文格式标准（GB/T 9704-2012）：');
  console.log('  页边距：上37mm，下35mm，左28mm，右26mm（A4）');
  console.log('  作品名称：方正小标宋简体，2号（22pt），居中');
  console.log('  一级标题：黑体3号，二级标题：楷体3号，三/四级：仿宋3号');
  console.log('  正文：仿宋GB2312，3号（16pt），行距28.9磅，每页22行');
  console.log('');

  const result = await generateDoc(markdownPath, outputPath, imagePaths);

  console.log('');
  if (result) {
    console.log(`输出文件: ${outputPath}`);
  } else {
    console.log('生成失败');
    process.exit(1);
  }
}

main().catch(console.error);
