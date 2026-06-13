TSCONFIG = '''{
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
}'''

SERVER_TS = '''import { watch, mkdirSync, existsSync } from "fs";
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
const sockets = new Set<any>();

const notifyReload = () => {
  console.log("\\u{1F504} File changed! Reloading browser...");
  for (const socket of sockets) { socket.send("reload"); }
};

if (!existsSync("./dist")) mkdirSync("./dist", { recursive: true });
watch("./dist", { recursive: true }, notifyReload);
watch("./index.html", notifyReload);

Bun.serve({
  port: PORT,
  fetch(req: Request, server: any) {
    const url = new URL(req.url);
    if (url.pathname === "/ws") {
      if (server.upgrade(req)) return;
      return new Response("Upgrade failed", { status: 400 });
    }
    let filePath = "." + url.pathname;
    if (filePath === "./") filePath = "./index.html";
    try {
      return new Response(Bun.file(filePath));
    } catch {
      try { return new Response(Bun.file("./index.html")); }
      catch { return new Response("404 Not Found", { status: 404 }); }
    }
  },
  websocket: {
    open(ws: any) { sockets.add(ws); },
    close(ws: any) { sockets.delete(ws); }
  }
});
console.log(`\\u{1F30D} Bun Live Server running at http://localhost:${PORT}`);
'''

INDEX_TS = {
    "default": '''const app = document.getElementById('app');
if (app) {
  app.innerHTML = `
    <h1>✨ Bun + TypeScript Environment</h1>
    <p>Ready to develop! Edit <code>src/index.ts</code> to get started.</p>
  `;
}''',

    "tailwind": '''const app = document.getElementById('app');
if (app) {
  app.innerHTML = `
    <div class='max-w-md p-8 bg-slate-800 rounded-2xl border border-slate-700 shadow-xl text-center'>
      <h1 class='text-3xl font-black mb-3 bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent'>Tailwind Ready</h1>
      <p class='text-slate-400'>Edit <code class='bg-slate-950 text-rose-400 px-1.5 py-0.5 rounded text-sm font-mono'>src/index.ts</code> to start building your UI.</p>
    </div>
  `;
}''',

    "router": '''// ⚡ 自作SPAルーターの基本実装
const routes: Record<string, string> = {
  '/': '<div class="text-center"><h1 class="text-3xl font-bold text-sky-400 mb-2">Home Page</h1><p class="text-slate-400">Welcome to the lightweight SPA initial template!</p></div>',
  '/about': '<div class="text-center"><h1 class="text-3xl font-bold text-indigo-400 mb-2">About Page</h1><p class="text-slate-400">This router operates using pure HTML5 History API.</p></div>',
  '/setting': '<div class="text-center"><h1 class="text-3xl font-bold text-emerald-400 mb-2">Setting Page</h1><p class="text-slate-400">Configure your system parameters here.</p></div>'
};

const render = (path: string) => {
  const app = document.getElementById('app');
  if (app) app.innerHTML = routes[path] || '<h1 class="text-2xl font-bold text-rose-500">404 Not Found</h1>';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    link.classList.toggle('text-sky-400', href === path);
    link.classList.toggle('text-slate-400', href !== path);
  });
};

const navigate = (path: string) => { window.history.pushState({}, '', path); render(path); };

window.addEventListener('popstate', () => render(window.location.pathname));
document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;
  if (target.matches('.nav-link')) {
    e.preventDefault();
    const href = target.getAttribute('href');
    if (href) navigate(href);
  }
});

render(window.location.pathname);''',

    "empty": "console.log('Hello TypeScript!');",
}

DESTYLE_CDN = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/destyle.css@3.0.2/destyle.min.css">'
TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'

DEFAULT_STYLES = """  <style>
    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: grid; place-items: center; min-height: 100vh; margin: 0; }
    #app { text-align: center; }
    h1 { font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    p { color: #94a3b8; font-size: 1.1rem; }
    code { background-color: #1e293b; padding: 0.2rem 0.4rem; border-radius: 0.25rem; color: #f43f5e; font-family: monospace; }
  </style>"""

HOTRELOAD_SCRIPT = """  <script>
    const ws = new WebSocket('ws://' + location.host + '/ws');
    ws.onmessage = (e) => { if(e.data === 'reload') location.reload(); };
  </script>"""


def get_html(mode: str, title: str) -> str:
    if mode == "tailwind":
        cdn = TAILWIND_CDN
        styles = ""
        body_class = ' class="bg-slate-900 text-slate-100 min-h-screen grid place-items-center font-sans"'
        body_content = '  <div id="app"></div>'
    elif mode == "router":
        cdn = TAILWIND_CDN
        styles = ""
        body_class = ' class="bg-slate-900 text-slate-100 min-h-screen font-sans flex flex-col"'
        body_content = """  <nav class="bg-slate-950 border-b border-slate-800 px-6 py-4 flex gap-6">
    <a href="/" class="nav-link text-sky-400 font-bold hover:text-sky-300">\U0001f3e0 Home</a>
    <a href="/about" class="nav-link text-slate-400 font-bold hover:text-slate-200">\U0001f4c4 About</a>
    <a href="/setting" class="nav-link text-slate-400 font-bold hover:text-slate-200">⚙️ Setting</a>
  </nav>
  <main id="app" class="flex-1 grid place-items-center p-6"></main>"""
    elif mode == "empty":
        cdn = ""
        styles = ""
        body_class = ""
        body_content = '  <div id="app"></div>'
    else:  # default
        cdn = DESTYLE_CDN
        styles = DEFAULT_STYLES
        body_class = ""
        body_content = '  <div id="app"></div>'

    cdn_line = f"\n  {cdn}" if cdn else ""
    styles_line = f"\n{styles}" if styles else ""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>{cdn_line}{styles_line}
</head>
<body{body_class}>
{body_content}
  <script type="module" src="./dist/index.js"></script>
{HOTRELOAD_SCRIPT}
</body>
</html>"""
