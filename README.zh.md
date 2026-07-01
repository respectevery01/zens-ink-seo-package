<div align="center">

# zens.ink

### 免费 SEO 关键词研究工具包

面向独立开发者的命令行工具。零依赖，纯 Python。

[English](README.md) · [中文](README.zh.md)

</div>

---

七个命令行工具，覆盖完整的 SEO 流程 —— 从关键词研究到技术审计。不需要付费 API，不需要 Ahrefs，不需要订阅。只用免费数据源 + Python 标准库。

| 工具 | 功能 | 需要密钥 |
|------|------|---------|
| `keyword_research` | 通过 Google 自动补全发现用户搜索什么 | 无 |
| `keyword_volume` | 通过 Bing 站长 API 获取真实搜索量 | 免费 Bing key |
| `kd` | 基于 SERP 结构分析关键词难度 | 免费 Serper key |
| `brave_volume` | 通过 Brave SERP 信号估算搜索需求 | 免费 Brave key |
| `search_performance` | 你在 Google 上的真实排名数据 | 免费 GSC OAuth |
| `competitor_gap` | 通过 sitemap 分析竞品内容 | 无 |
| `site_audit` | 技术 SEO 审计：断链、孤岛页面、缺失标签 | 无 |

## 为什么做这个

Ahrefs 每月 $200，SEMrush 每月 $130。对独立开发者来说，只是做关键词研究，太贵了。

zens.ink 把免费公开数据源 —— Google 自动补全、Bing 站长工具、Google Search Console —— 串在一起，零 Python 依赖。

## 快速开始

```bash
git clone https://github.com/respectevery01/zens-ink-seo-package.git
cd zens-ink-seo-package

# 发现关键词
python3 -m zens_ink.keyword_research "塔罗牌" --lang zh --expand

# 查搜索量
python3 -m zens_ink.keyword_volume "塔罗牌" --country cn --lang zh-CN

# 分析竞品
python3 -m zens_ink.competitor_gap --url https://example.com/sitemap.xml

# 审计构建产物的 SEO 问题
python3 -m zens_ink.site_audit --dist dist --sitemap dist/sitemap.xml

# 查看自己站点的搜索表现
python3 -m zens_ink.search_performance
```

## 环境要求

- Python 3.10+
- 无需 pip install — 纯标准库实现

## 文档

完整案例和 Pro 增值包见 [zens.ink](https://zens.ink)

## 开源协议

MIT — 个人和商业项目均可自由使用。

---

<div align="center">

Made by [Jask](https://github.com/respectevery01)

</div>
