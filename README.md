<div align="center">
  <br>
  <img src="https://img.shields.io/badge/DataGuard-v1.0-orange?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/status-active-success?style=flat-square" alt="status">
  <img src="https://img.shields.io/badge/stack-vanilla_JS-ff69b4?style=flat-square" alt="stack">
  <img src="https://img.shields.io/badge/deploy-GitHub_Pages-blue?style=flat-square" alt="deploy">
  <br><br>
</div>

# 📡 DataGuard — 数据余量智能监控系统

> **数据如流水，余量需看清。**  
> DataGuard 是一个生产级的数据用量实时监控看板。它自动登录运营商门户，抓取数据余量，并以精美的可视化仪表盘呈现——不只是告诉你"用了多少"，更是**预警你"还剩多少"**。

---

## 🌟 核心理念

**传统的数据用量查询是过去导向的：**
```
你用了 86.7 GB
```

**DataGuard 是未来导向的：**
```
你剩余 13.3 GB
按当前速度，约 5 天后数据耗尽 ⚠️
```

这不是一个简单的"查流量"工具，而是一个**资源管理仪表盘**。就像家里的电表水表——它让你对消耗有感知，对稀缺有预警，对行为有反馈。

---

## ✨ 功能特性

| 特性 | 说明 |
|---|---|
| **🎯 余量优先** | 巨幅数字展示**剩余量**而非已用量，一眼掌握资源状况 |
| **🧠 智能预测** | 基于历史消耗自动计算日均用量，预测**数据耗尽天数** |
| **📈 微型趋势图** | Sparkline 曲线直观展示余量变化趋势，消耗速度一目了然 |
| **🚦 三色预警** | 🟢 充足 (>30GB) / 🟡 注意 (10-30GB) / 🔴 紧急 (<10GB) |
| **🎨 渐变色进度条** | 绿→橙→红渐变，视觉紧迫感随余量递减递增 |
| **📊 余量历史** | 最近4次数据快照对比，日间/午夜双计划同框 |
| **📱 全平台适配** | 桌面双栏看板 + 手机单栏自适应，一页全览无需滚动 |
| **🤖 自动运行** | GitHub Actions 每6小时自动抓取，零人工干预 |

---

## 🏗 架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  CSL Portal  │ ──▶ │  Scraper     │ ──▶ │  history.json│
│  (prepaid.   │     │  (Playwright)│     │  (数据存储)  │
│   hkcsl.com) │     │              │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  GitHub      │ ◀── │  GitHub      │ ◀── │  DataGuard   │
│  Pages       │     │  Actions     │     │  Dashboard   │
│  (发布)      │     │  (定时抓取)   │     │  (可视化)    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### 技术栈

| 层 | 技术 |
|---|---|
| **前端** | 纯 HTML + CSS + JavaScript（单个文件，零依赖） |
| **可视化** | 原生 SVG 微线图 + CSS 渐变进度条 |
| **爬虫** | Python + Playwright（无头浏览器自动化） |
| **调度** | GitHub Actions（Cron 表达式，当前每6小时） |
| **托管** | GitHub Pages（完全免费，全球 CDN） |
| **数据** | JSON 文件 + Git 版本管理 |

> 为什么没有用 React / Vue / 任何框架？  
> 因为一个看板页面不需要。纯静态方案：零构建、零依赖、零维护成本、永不报错。  
> 这恰恰是生产级产品的核心原则——**用最合适的技术，而不是最多的技术**。

---

## 🚀 快速开始

### 1. Fork 这个仓库

```bash
git clone https://github.com/YOUR_USERNAME/csl-usage.git
cd csl-usage
```

### 2. 配置凭证

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加：

| Secret | 值 | 说明 |
|---|---|---|
| `CSL_USER` | `59985735` | 你的 CSL 手机号码 |
| `CSL_PASS` | `032022` | 你的 CSL 门户密码 |

> 密码存储在 GitHub 加密 Secrets 中，不会泄露到代码里。

### 3. 开启 GitHub Pages

仓库 **Settings → Pages** → Deploy from `master` → folder `/docs` → Save

### 4. 手动触发首次抓取

仓库 **Actions** → **Scrape CSL Usage** → **Run workflow**

### 5. 打开看板

访问 `https://YOUR_USERNAME.github.io/csl-usage`

---

## ⚙️ 自定义配置

### 更新频率

编辑 `.github/workflows/scrape.yml` 中的 cron 表达式：

```yaml
- cron: '0 */6 * * *'   # 每6小时（默认）
- cron: '0 */2 * * *'   # 每2小时
- cron: '0 8 * * *'     # 每天早8点
```

> cron 为 UTC 时间。香港 = UTC+8。

### 数据计划总量

爬虫会自动从计划名中提取总量（如 `100GB@42Mbps` 中的 `100`）。  
如果需要手动覆盖，编辑 `scraper.py` 中的 `total_gb` 逻辑。

---

## 📁 项目结构

```
csl-usage/
├── .github/
│   └── workflows/
│       └── scrape.yml         # GitHub Actions 定时任务
├── scripts/
│   └── scraper.py             # Playwright 自动登录 + 数据提取
├── docs/
│   ├── index.html             # DataGuard 看板（前端页面）
│   └── data/
│       └── history.json       # 历史数据快照
└── README.md
```

---

## 🧠 设计哲学

### 余量 = 焦虑

人天生对"还剩多少"比"用了多少"更敏感。  
- 电表显示**剩余电量**，不是已用电量  
- 油表显示**剩余油量**，不是已用油量  
- DataGuard 显示**剩余流量**，不是已用流量  

### 预测 = 行动力

"86.7 GB 已用"不会让你行动。  
"按此速度，约 5 天后耗尽"会。

### 渐变 = 紧迫感

绿色让人放松，黄色让人注意，红色让人行动。  
DataGuard 的色彩系统不是一个装饰——它是一个**情绪触发器**。

---

## 📄 许可证

MIT License

---

<div align="center">
  <sub>Built with ❤️ for people who want to stay in control of their data.</sub>
</div>
