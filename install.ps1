# 💡 インストールを実行するPowerShellスクリプト
$functionName = "tssetup"
$functionCode = @'
function tssetup {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $false, Position = 0)][string]$ProjectName,
        [Parameter(Mandatory = $false)][string]$Title = "Bun + TS App",
        [Parameter(Mandatory = $false)]
        [ValidateSet("default", "tailwind", "router", "empty")]
        [string]$Mode = "default",
        [Parameter(Mandatory = $false)][switch]$Help,
        [Parameter(Mandatory = $false)][switch]$Code,
        [Parameter(Mandatory = $false)][switch]$Uninstall
    )

    if ($Uninstall) {
        Write-Host ""
        Write-Host "⚠ tssetup をアンインストールします。本当によろしいですか？ (y/N): " -NoNewline -ForegroundColor Yellow
        $confirm = Read-Host
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "キャンセルしました。" -ForegroundColor DarkGray
            return
        }
        $profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
        $n = "tssetup"
        if ($profileContent -match "# <<BEGIN:${n}>>") {
            $profileContent = $profileContent -replace "(?s)`n?# <<BEGIN:${n}>>.*?# <<END:${n}>>", ""
            [System.IO.File]::WriteAllText($PROFILE, $profileContent.Trim(), [System.Text.UTF8Encoding]::new($true))
            Remove-Item Function:tssetup -ErrorAction SilentlyContinue
            Write-Host "✅ tssetup をアンインストールしました。" -ForegroundColor Green
        } else {
            Write-Host "⚠ tssetup はインストールされていません。" -ForegroundColor Yellow
        }
        return
    }

    $localVersion = "1.0.1"
    $remoteVersion = $null
    try {
        $remoteVersion = (irm https://raw.githubusercontent.com/Lapius7/tssetup/main/version.txt -TimeoutSec 3 -ErrorAction Stop).Trim()
        if ($remoteVersion -ne $localVersion) {
            Write-Host "🔄 新しいバージョン ($remoteVersion) があります。自動更新しています..." -ForegroundColor Yellow
            irm https://raw.githubusercontent.com/Lapius7/tssetup/main/install.ps1 | iex
            Write-Host "✅ 更新完了！もう一度コマンドを実行してください。" -ForegroundColor Green
            return
        }
    } catch {}

    if ([string]::IsNullOrEmpty($ProjectName) -and -not $Help) {
        Write-Host ""
        Write-Host "🎨 tssetup" -ForegroundColor Cyan -NoNewline; Write-Host "  v$localVersion" -ForegroundColor DarkGray
        Write-Host "Bun + TypeScript フロントエンド環境を1コマンドで構築するツール"
        Write-Host ""
        Write-Host "開発者  : " -NoNewline -ForegroundColor Yellow; Write-Host "Lapius7"
        Write-Host "X       : " -NoNewline -ForegroundColor Yellow; Write-Host "https://x.com/Lapius7"
        Write-Host "GitHub  : " -NoNewline -ForegroundColor Yellow; Write-Host "https://github.com/Lapius7/tssetup"
        Write-Host ""
        if ($null -ne $remoteVersion) {
            if ($remoteVersion -eq $localVersion) {
                Write-Host "バージョン  : $localVersion  " -NoNewline; Write-Host "✅ 最新です" -ForegroundColor Green
            } else {
                Write-Host "バージョン  : $localVersion  " -NoNewline; Write-Host "⬆ 最新: $remoteVersion" -ForegroundColor Yellow
            }
        } else {
            Write-Host "バージョン  : $localVersion  " -NoNewline; Write-Host "(バージョン確認失敗)" -ForegroundColor DarkGray
        }
        Write-Host ""
        Write-Host "使い方  : tssetup <プロジェクト名> [-Mode <モード>]" -ForegroundColor DarkGray
        Write-Host "ヘルプ  : tssetup -Help" -ForegroundColor DarkGray
        Write-Host ""
        return
    }

    if ($Help) {
        Write-Host "`n🎨 [tssetup] コマンドヘルプ" -ForegroundColor Cyan
        Write-Host "==================================================" -ForegroundColor DarkGray
        Write-Host "簡単にBun + TypeScriptのフロントエンド開発環境を構築します。"
        Write-Host "`n使い方:" -ForegroundColor Yellow
        Write-Host "  tssetup <プロジェクト名> [-Mode <モード名>] [-Title <タイトル>] [-Code]"
        Write-Host "`nオプション:" -ForegroundColor Yellow
        Write-Host "  -Mode [default]  : 標準テンプレート (Destyle.css内包・ダーク系)"
        Write-Host "  -Mode [tailwind] : Tailwind CSS 組み込み (即開発可能レイアウト)"
        Write-Host "  -Mode [router]   : ⚡ライブラリ不使用・自作SPAルーティング構成"
        Write-Host "  -Mode [empty]    : 最少構成（空のTSファイルとシンプルなHTML）"
        Write-Host "  -Title           : HTMLの <title> タグに設定する文字列"
        Write-Host "  -Code            : セットアップ完了後、新しいVS Codeのウィンドウで開く"
        Write-Host "  -Help            : このヘルプを表示します"
        Write-Host "`n📁 作成されるファイル構成:" -ForegroundColor Yellow
        Write-Host "  <プロジェクト名>/"
        Write-Host "  ├── src/"
        Write-Host "  │   └── index.ts        " -NoNewline; Write-Host "← エントリポイント（モード別で内容が異なる）" -ForegroundColor DarkGray
        Write-Host "  ├── dist/               " -NoNewline; Write-Host "← コンパイル後JS（tsc が自動生成）" -ForegroundColor DarkGray
        Write-Host "  ├── node_modules/       " -NoNewline; Write-Host "← bun install が自動生成" -ForegroundColor DarkGray
        Write-Host "  ├── index.html          " -NoNewline; Write-Host "← フロントエンドHTML" -ForegroundColor DarkGray
        Write-Host "  ├── server.ts           " -NoNewline; Write-Host "← 開発サーバー（ホットリロード対応）" -ForegroundColor DarkGray
        Write-Host "  ├── tsconfig.json       " -NoNewline; Write-Host "← TypeScript設定" -ForegroundColor DarkGray
        Write-Host "  └── package.json        " -NoNewline; Write-Host "← Bunプロジェクト設定" -ForegroundColor DarkGray
        Write-Host "==================================================`n" -ForegroundColor DarkGray
        return
    }
    
    New-Item -ItemType Directory -Path "$ProjectName/src" -Force > $null
    Set-Location $ProjectName

    Write-Host ""
    Write-Host "🔨 " -NoNewline -ForegroundColor Cyan
    Write-Host $ProjectName -NoNewline -ForegroundColor White
    Write-Host " を構築中..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  📁 src/ フォルダを作成しました" -ForegroundColor DarkGray

    bun init -y > $null
    if (Test-Path "index.ts") { Remove-Item "index.ts" -Force }
    Write-Host "  📦 package.json" -NoNewline; Write-Host "   (bun init)" -ForegroundColor DarkGray

    $tsconfig = '{
  "compilerOptions": {
    "rootDir": "./src",
    "outDir": "./dist",
    "target": "es2020",
    "module": "es2020",
    "moduleResolution": "node",
    "lib": ["es2020", "dom"],
    "strict": true,
    "skipLibCheck": true,
    "isolatedModules": true
  },
  "include": ["src"]
}'
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "tsconfig.json"), $tsconfig, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  ✅ tsconfig.json" -ForegroundColor Green

$serverTs = 'import { watch } from "fs";
const DEFAULT_PORT = 53000;

async function findAvailablePort(startPort: number): Promise<number> {
  let port = startPort;
  while (port <= 65535) {
    try {
      const server = Bun.serve({ port, fetch() { return new Response(); } });
      server.stop();
      return port;
    } catch { port++; }
  }
  return startPort;
}

const PORT = await findAvailablePort(DEFAULT_PORT);
const sockets = new Set();

const notifyReload = () => {
  console.log("🔄 File changed! Reloading browser...");
  for (const socket of sockets) { socket.send("reload"); }
};
watch("./dist", { recursive: true }, notifyReload);
watch("./index.html", notifyReload);

Bun.serve({
  port: PORT,
  fetch(req, server) {
    const url = new URL(req.url);
    if (url.pathname === "/ws") {
      if (server.upgrade(req)) return;
      return new Response("Upgrade failed", { status: 400 });
    }
    let filePath = "." + url.pathname;
    if (filePath === "./") filePath = "./index.html";
    try {
      const file = Bun.file(filePath);
      return new Response(file);
    } catch {
      try {
        return new Response(Bun.file("./index.html"));
      } catch {
        return new Response("404 Not Found", { status: 404 });
      }
    }
  },
  websocket: {
    open(ws) { sockets.add(ws); },
    close(ws) { sockets.delete(ws); }
  }
});
console.log(`🌍 Bun Live Server running at http://localhost:${PORT}`);
'
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "server.ts"), $serverTs, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  ✅ server.ts" -ForegroundColor Green

$cdn ="<link rel=""stylesheet"" href=""https://cdn.jsdelivr.net/npm/destyle.css@3.0.2/destyle.min.css"">"
$styles = "  <style>`n    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: grid; place-items: center; min-height: 100vh; margin: 0; }`n    #app { text-align: center; }`n    h1 { font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }`n    p { color: #94a3b8; font-size: 1.1rem; }`n    code { background-color: #1e293b; padding: 0.2rem 0.4rem; border-radius: 0.25rem; color: #f43f5e; font-family: monospace; }`n  </style>"
$bodyClass = ""
$bodyHtml = "  <div id=""app""></div>"
$bq = [char]96

switch ($Mode) {
  "empty" {
    $cdn = ""; $styles = ""
    $tsLines = @("console.log('Hello TypeScript!');")
  }
  "tailwind" {
    $cdn = "<script src=""https://cdn.tailwindcss.com""></script>"
    $styles = ""
    $bodyClass = " class=""bg-slate-900 text-slate-100 min-h-screen grid place-items-center font-sans"""
    $tsLines = @(
      "const app = document.getElementById('app');"
      "if (app) {"
      "  app.innerHTML = ${bq}"
      "    <div class='max-w-md p-8 bg-slate-800 rounded-2xl border border-slate-700 shadow-xl text-center'>"
      "      <h1 class='text-3xl font-black mb-3 bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent'>Tailwind Ready</h1>"
      "      <p class='text-slate-400'>Edit <code class='bg-slate-950 text-rose-400 px-1.5 py-0.5 rounded text-sm font-mono'>src/index.ts</code> to start building your UI.</p>"
      "    </div>"
      "  ${bq};"
      "}"
    )
  }
  "router" {
    $cdn = "<script src=""https://cdn.tailwindcss.com""></script>"
    $styles = ""
    $bodyClass = " class=""bg-slate-900 text-slate-100 min-h-screen font-sans flex flex-col"""
    $bodyHtml = "  `n  <nav class='bg-slate-950 border-b border-slate-800 px-6 py-4 flex gap-6'>`n    <a href='/' class='nav-link text-sky-400 font-bold hover:text-sky-300'>🏠 Home</a>`n    <a href='/about' class='nav-link text-slate-400 font-bold hover:text-slate-200'>📄 About</a>`n    <a href='/setting' class='nav-link text-slate-400 font-bold hover:text-slate-200'>⚙️ Setting</a>`n  </nav>`n  `n  <main id='app' class='flex-1 grid place-items-center p-6'></main>"
            
    $tsLines = @(
      "// ⚡ 自作SPAルーターの基本実装"
      "const routes: Record<string, string> = {"
      "  '/': '<div class=""text-center""><h1 class=""text-3xl font-bold text-sky-400 mb-2"">Home Page</h1><p class=""text-slate-400"">Welcome to the lightweight SPA initial template!</p></div>',"
      "  '/about': '<div class=""text-center""><h1 class=""text-3xl font-bold text-indigo-400 mb-2"">About Page</h1><p class=""text-slate-400"">This router operates using pure HTML5 History API.</p></div>',"
      "  '/setting': '<div class=""text-center""><h1 class=""text-3xl font-bold text-emerald-400 mb-2"">Setting Page</h1><p class=""text-slate-400"">Configure your system parameters here.</p></div>'"
      "};"
      ""
      "const render = (path: string) => {"
      "  const app = document.getElementById('app');"
      "  if (app) app.innerHTML = routes[path] || '<h1 class=""text-2xl font-bold text-rose-500"">404 Not Found</h1>';"
      "  "
      "  document.querySelectorAll('.nav-link').forEach(link => {"
      "    const href = link.getAttribute('href');"
      "    if (href === path) {"
      "      link.classList.replace('text-slate-400', 'text-sky-400');"
      "    } else {"
      "      link.classList.replace('text-sky-400', 'text-slate-400');"
      "    }"
      "  });"
      "};"
      ""
      "const navigate = (path: string) => {"
      "  window.history.pushState({}, '', path);"
      "  render(path);"
      "};"
      ""
      "window.addEventListener('popstate', () => render(window.location.pathname));"
      ""
      "document.addEventListener('click', (e) => {"
      "  const target = e.target as HTMLElement;"
      "  if (target.matches('.nav-link')) {"
      "    e.preventDefault();"
      "    const href = target.getAttribute('href');"
      "    if (href) navigate(href);"
      "  }"
      "});"
      ""
      "render(window.location.pathname);"
    )
  }
  default {
    $tsLines = @(
      "const app = document.getElementById('app');"
      "if (app) {"
      "  app.innerHTML = ${bq}"
      "    <h1>✨ Bun + TypeScript Environment</h1>"
      "    <p>Ready to develop! Edit <code>src/index.ts</code> to get started.</p>"
      "  ${bq};"
      "}"
    )
  }
}

$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "src/index.ts"), ($tsLines -join "`n"), $utf8NoBom)
    Write-Host "  ✅ src/index.ts" -ForegroundColor Green
$html ="<!DOCTYPE html>`n<html lang=""ja"">`n<head>`n  <meta charset=""UTF-8"">`n  <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">`n  <title>$Title</title>`n  $cdn`n$styles`n</head>`n<body$bodyClass>`n$bodyHtml`n  <script type=""module"" src=""./dist/index.js""></script>`n  <script>`n    const ws = new WebSocket('ws://' + location.host + '/ws');`n    ws.onmessage = (e) => { if(e.data === 'reload') location.reload(); };`n  </script>`n</body>`n</html>"
[System.IO.File]::WriteAllText((Join-Path (Get-Location) "index.html"), $html, $utf8NoBom)
    Write-Host "  ✅ index.html" -ForegroundColor Green

    Write-Host ""
    Write-Host "  ──────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "  ✨ " -NoNewline
    Write-Host $ProjectName -NoNewline -ForegroundColor Cyan
    Write-Host "  セットアップ完了！" -ForegroundColor Green
    Write-Host "  ──────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  📁 $ProjectName/" -ForegroundColor Yellow
    Write-Host "  ├── src/"
    Write-Host "  │   └── index.ts"
    Write-Host "  ├── dist/               " -NoNewline; Write-Host "← tsc が自動生成" -ForegroundColor DarkGray
    Write-Host "  ├── index.html"
    Write-Host "  ├── server.ts"
    Write-Host "  ├── tsconfig.json"
    Write-Host "  └── package.json"
    Write-Host ""
    Write-Host "  📂 $(Get-Location)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  🚀 次のステップ:" -ForegroundColor Cyan
    Write-Host "     tsbuild" -NoNewline -ForegroundColor White
    Write-Host "    開発サーバーを起動" -ForegroundColor DarkGray
    Write-Host ""
    if ($Code -and (Get-Command code -ErrorAction SilentlyContinue)) { code . }
}
'@

if (!(Test-Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force > $null
}

$profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ([string]::IsNullOrEmpty($profileContent)) { $profileContent = "" }

$beginMarker = "# <<BEGIN:$functionName>>"
$endMarker = "# <<END:$functionName>>"
$markerPattern = "(?s)# <<BEGIN:$functionName>>.*# <<END:$functionName>>"

if ($profileContent -match $markerPattern) {
    $profileContent = $profileContent -replace $markerPattern, ""
}
$profileContent = $profileContent.Replace("# <<END:$functionName>>", "").Trim()

if (-not ($profileContent -match "# <<BEGIN:$functionName>>") -and $profileContent -match "function\s+$functionName\b") {
    Write-Host ""
    Write-Host "⚠ 警告: マーカーのない旧バージョンの $functionName がプロファイルに存在します。" -ForegroundColor Yellow
    Write-Host "  自動削除は行いません。以下を手動で実行してください：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1. メモ帳でプロファイルを開く：" -ForegroundColor Cyan
    Write-Host "     notepad `$PROFILE" -ForegroundColor White
    Write-Host "  2. 'function $functionName' から始まるブロックを手動で削除する" -ForegroundColor Cyan
    Write-Host "  3. 保存後にこのインストールコマンドを再実行する" -ForegroundColor Cyan
    Write-Host ""
    return
}

$block = "$beginMarker`n$functionCode`n$endMarker"
$newProfileContent = $profileContent.Trim() + "`n`n" + $block
[System.IO.File]::WriteAllText($PROFILE, $newProfileContent.Trim(), [System.Text.UTF8Encoding]::new($true))

# 即時反映のためにメモリ上の関数も更新する
Invoke-Expression $functionCode

Write-Host "✨ tssetup コマンドのインストール/更新が完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "📦 インストールコマンド（再インストール・更新時）:" -ForegroundColor Cyan
Write-Host "  irm https://raw.githubusercontent.com/Lapius7/tssetup/main/install.ps1 | iex"
Write-Host ""
Write-Host "📋 使い方:" -ForegroundColor Cyan
Write-Host "  tssetup <プロジェクト名> [-Mode <モード>] [-Title <タイトル>] [-Code]"
Write-Host ""
Write-Host "  tssetup myapp                         " -NoNewline; Write-Host "# 標準テンプレートで作成" -ForegroundColor DarkGray
Write-Host "  tssetup myapp -Mode tailwind          " -NoNewline; Write-Host "# Tailwind CSS 組み込み" -ForegroundColor DarkGray
Write-Host "  tssetup myapp -Mode router            " -NoNewline; Write-Host "# 自作SPA ルーター構成" -ForegroundColor DarkGray
Write-Host "  tssetup myapp -Mode empty             " -NoNewline; Write-Host "# 最小構成" -ForegroundColor DarkGray
Write-Host "  tssetup myapp -Title ""My App"" -Code  " -NoNewline; Write-Host "# タイトル指定 + VS Code 起動" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📁 作成されるファイル構成:" -ForegroundColor Cyan
Write-Host "  <プロジェクト名>/"
Write-Host "  ├── src/"
Write-Host "  │   └── index.ts        " -NoNewline; Write-Host "← エントリポイント（モード別で内容が異なる）" -ForegroundColor DarkGray
Write-Host "  ├── dist/               " -NoNewline; Write-Host "← コンパイル後JS（tsc が自動生成）" -ForegroundColor DarkGray
Write-Host "  ├── node_modules/       " -NoNewline; Write-Host "← bun install が自動生成" -ForegroundColor DarkGray
Write-Host "  ├── index.html          " -NoNewline; Write-Host "← フロントエンドHTML" -ForegroundColor DarkGray
Write-Host "  ├── server.ts           " -NoNewline; Write-Host "← 開発サーバー（ホットリロード対応）" -ForegroundColor DarkGray
Write-Host "  ├── tsconfig.json       " -NoNewline; Write-Host "← TypeScript設定" -ForegroundColor DarkGray
Write-Host "  └── package.json        " -NoNewline; Write-Host "← Bunプロジェクト設定" -ForegroundColor DarkGray
Write-Host ""
Write-Host "新しいPowerShellウィンドウを開くか、 '. `$PROFILE' を実行して即時反映させてください。" -ForegroundColor Yellow
