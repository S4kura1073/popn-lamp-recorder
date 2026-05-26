# popn-lamp-recorder — pop'n music 点灯追踪工具

## 项目已成功部署在[popn-lamp-recorder](https://popn-lamp-recorder.netlify.app/) 直接前往链接保存为PWA即可使用

记录你在 [pop'n music](https://p.eagate.573.jp/game/popn/) 中每首曲子的通关状态（点灯），支持按等级/难易度/代数/点灯状态筛选、本地持久化，以及数据备份恢复。

## 项目结构

```
popn-lamp-recorder/
├── scraper/          # Python 爬虫，从 popn.wiki 抓取难易度表
├── data/             # 爬虫输出的原始数据（JSON / CSV）
└── popn-tracker/     # Vue 3 前端 PWA，点灯追踪主体
```

## 点灯状态说明

| 状态 | 颜色 | 含义 |
|------|------|------|
| NoPlay | 灰蓝 | 未游玩 |
| Failed | 灰黑 | 已游玩但 FAILED |
| NormalClear | 铜色 | 通关（CLEAR） |
| FullCombo | 银色 | 全连（FULL COMBO） |
| Perfect | 金色 | 完美通关（PERFECT） |

---

## 前端应用（popn-tracker）

### 准备工作

安装 [Node.js](https://nodejs.org/) 18 或更高版本，然后进入前端目录安装依赖：

```bash
cd popn-tracker
npm install
```

---

### 本地开发

```bash
npm run dev
```

终端会显示如下内容，浏览器访问 `http://localhost:5173` 即可预览：

```
VITE v6.x.x  ready in 300ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

保存文件后页面会自动热更新，无需手动刷新。

> 开发模式下 Service Worker 未启用，刷新后不会走离线缓存，仅用于调试界面。

---

### 手机局域网访问（开发调试）

将电脑和手机连在**同一 Wi-Fi**，启动时附加 `--host` 参数：

```bash
npm run dev -- --host
```

终端会额外显示局域网地址，例如：

```
➜  Local:    http://localhost:5173/
➜  Network:  http://192.168.1.100:5173/
```

手机浏览器直接访问 Network 地址即可。

---

### 构建生产版本

```bash
npm run build
```

构建完成后产物输出到 `popn-tracker/dist/`。可本地预览验证：

```bash
npm run preview
# 浏览器访问 http://localhost:4173
```

此时 PWA 功能（离线缓存、安装到桌面）均已启用，可测试安装体验。

---

### 部署到公网 — GitHub Pages

> 部署到 HTTPS 域名后，才能在手机上正式安装为 PWA。

**第一步：设置 base 路径（如果不是根域名）**

如果你的访问地址是 `https://用户名.github.io/仓库名/`（而不是根路径），需要在 `popn-tracker/vite.config.ts` 中添加 `base` 配置：

```ts
export default defineConfig({
  base: '/仓库名/',   // 替换为你的 GitHub 仓库名
  // ...其余配置不变
})
```

如果使用自定义域名或 `用户名.github.io` 根路径部署，则跳过此步。

**第二步：构建**

```bash
cd popn-tracker
npm run build
```

**第三步：将 dist/ 推送到 gh-pages 分支**

```bash
cd dist
git init
git add -A
git commit -m "deploy"
git push -f https://github.com/你的用户名/仓库名.git main:gh-pages
```

**第四步：在 GitHub 仓库设置中启用 Pages**

进入仓库页面 → **Settings** → **Pages** → Source 选择 `gh-pages` 分支 → **Save**。

稍等 1～2 分钟后，访问 `https://你的用户名.github.io/仓库名/` 即可。

---

### 部署到公网 — Netlify

**方式一：拖拽上传（最快，无需账号绑定 GitHub）**

1. 运行 `npm run build` 生成 `dist/`
2. 打开 [Netlify Drop](https://app.netlify.com/drop)
3. 将 `popn-tracker/dist/` 文件夹整个拖入页面
4. 自动部署完成，获得一个 `xxx.netlify.app` 链接，本人已成功部署一个app，域名为"https://popn-lamp-recorder.netlify.app/"

**方式二：连接 GitHub 自动部署（推荐，每次推送代码自动更新）**

1. 登录 [Netlify](https://netlify.com)，点击 **Add new site → Import an existing project**
2. 授权并选择你的 GitHub 仓库
3. 填写构建配置：
   - **Base directory**：`popn-tracker`
   - **Build command**：`npm run build`
   - **Publish directory**：`popn-tracker/dist`
4. 点击 **Deploy site**，首次部署约 1 分钟完成
5. 后续每次 `git push` 都会自动触发重新部署

---

### 手机端安装为 PWA

将应用部署到 HTTPS 域名后，手机浏览器打开，按以下步骤安装为本地 App：

**iOS Safari**

1. 点击底部工具栏中间的**分享按钮**（方框+向上箭头图标）
2. 在弹出菜单中向下滚动，找到**"添加到主屏幕"**并点击
3. 确认应用名称，点击右上角**"添加"**

**Android Chrome**

1. 点击右上角**三点菜单**
2. 选择**"添加到主屏幕"**或**"安装应用"**
3. 点击弹窗中的**"安装"**确认

安装完成后从主屏幕启动，全屏运行，无浏览器地址栏，体验与原生 App 相同。  
PWA 安装后数据持久保存，**不受 Safari 7 天 localStorage 自动清理限制**。

---

### 数据备份与迁移

点灯数据存储在**设备本地 localStorage**，清除浏览器数据或更换设备前请先备份：

**导出（备份）**

在应用底部点击**"导出数据"** → 自动下载一个带日期的 JSON 文件，妥善保存。

**导入（恢复）**

在新设备打开应用，点击**"导入数据"** → 选择之前导出的 JSON 文件 → 数据自动恢复。

支持旧版本数据格式自动迁移，无需手动处理版本兼容问题。

---

## 爬虫（scraper）

从 [popn.wiki](https://popn.wiki) 抓取 Lv29～Lv50 难易度表，运行后自动写入 `data/` 和 `popn-tracker/public/` 两个位置。

### 运行环境

需要 Python 3.10 或更高版本。

**安装依赖**

```bash
cd scraper
pip install -r requirements.txt
```

**运行爬虫**

```bash
python scraper.py
```

运行完成后会同时更新以下两个文件：

- `data/popn_difficulty_table.json` — 原始数据存档
- `popn-tracker/public/popn_difficulty_table.json` — 前端静态资源（直接生效，无需手动复制）

> 爬虫内置 1.5～4 秒随机延迟防风控，完整爬取 Lv29～Lv50 约需 **3～5 分钟**。

## 本项目全程 vibe coding 完成，以自用为主，不会主动修复bug，请谅解！
