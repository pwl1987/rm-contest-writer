# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-07

### Added
- **Description-driven Mockup Generation**: Mockup templates (dashboard, data-visualization, etc.) are now matched by user's functional description keywords rather than track binding. Track only affects architecture diagram selection.
- **User-uploaded image support**: Users can upload their own images with AI-assisted layout and annotation guidance.
- **requirements.txt**: Dependencies pinned (`python-docx>=1.1.0,<2.0.0`, `lxml>=4.9.0`, `Pillow>=10.0.0`).

### Fixed
- **Image placeholder**: `add_image_paragraph` now inserts `[图片缺失: xxx]` when image file is missing.
- **Table title parsing**: Multi-format support added (`> 注：...`, `**表N：xxx**`, `表N：xxx`).

### Changed
- SKILL.md updated to reference Python scripts instead of Node.js (`generate-contest-docs.py`, `preflight-check.py`, `capture-diagram.py`).

## [1.0.0] - 2026-05-06

### Added
- Initial release with full 3-track support (技术研发类 / 应用创新类 / 内容创意类).
- SKILL.md with 7-step workflow (动态信息采集 → 方案评分 → 素材分析 → 撰写成稿 → Gate校验 → 去冗余优化 → Mockup嵌入).
- python-docx Word document generation with GB/T 9704-2012 compliance.
- 8 automated evaluation test cases.
