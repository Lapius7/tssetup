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
        [Parameter(Mandatory = $false)][switch]$Code
    )

    if ($Help -or ([string]::IsNullOrEmpty($ProjectName))) {
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

    bun init -y > $null
    if (Test-Path "index.ts") { Remove-Item "index.ts" -Force }

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
$tsconfig | Out-File -FilePath tsconfig.json -Encoding utf8

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
$serverTs | Out-File -FilePath server.ts -Encoding utf8

$cdn = "<link rel=""stylesheet"" href=""https://cdn.jsdelivr.net/npm/destyle.css@3.0.2/destyle.min.css"">"
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

$tsLines -join "`n" | Out-File -FilePath src/index.ts -Encoding utf8
$html = "<!DOCTYPE html>`n<html lang=""ja"">`n<head>`n  <meta charset=""UTF-8"">`n  <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">`n  <title>$Title</title>`n  $cdn`n$styles`n</head>`n<body$bodyClass>`n$bodyHtml`n  <script type=""module"" src=""./dist/index.js""></script>`n  <script>`n    const ws = new WebSocket('ws://' + location.host + '/ws');`n    ws.onmessage = (e) => { if(e.data === 'reload') location.reload(); };`n  </script>`n</body>`n</html>"
$html | Out-File -FilePath index.html -Encoding utf8

Write-Host "✨ TypeScript環境の構築が完了しました！ [$ProjectName]" -ForegroundColor Green
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
$markerPattern = "(?s)# <<BEGIN:$functionName>>.*?# <<END:$functionName>>"
$oldPattern = "(?s)function\s+$functionName\s*\{.*?\r?\n\}"

if ($profileContent -match $markerPattern) {
    $profileContent = $profileContent -replace $markerPattern, ""
} elseif ($profileContent -match $oldPattern) {
    $profileContent = $profileContent -replace $oldPattern, ""
}

$block = "$beginMarker`n$functionCode`n$endMarker"
$newProfileContent = $profileContent.Trim() + "`n`n" + $block
$newProfileContent.Trim() | Out-File -FilePath $PROFILE -Encoding utf8 -Force

# 即時反映のためにメモリ上の関数も更新する
Invoke-Expression $functionCode

Write-Host "✨ tssetup コマンドのインストール/更新が完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "📦 インストールコマンド（再インストール・更新時）:" -ForegroundColor Cyan
Write-Host "  powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`""
Write-Host ""
Write-Host "📋 使い方:" -ForegroundColor Cyan
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
