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
const START_PORT = parseInt(process.env.PORT ?? "53000");

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

const PORT = await findAvailablePort(START_PORT);
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

GITIGNORE = """node_modules/
dist/
.env
*.log
"""

INDEX_TS: dict = {
    "default": """const app = document.getElementById('app');
if (app) {
  app.innerHTML = `
    <h1>✨ Bun + TypeScript Environment</h1>
    <p>Ready to develop! Edit <code>src/index.ts</code> to get started.</p>
  `;
}""",

    "tailwind": """const app = document.getElementById('app');
if (app) {
  app.innerHTML = `
    <div class='max-w-md p-8 bg-slate-800 rounded-2xl border border-slate-700 shadow-xl text-center'>
      <h1 class='text-3xl font-black mb-3 bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent'>Tailwind Ready</h1>
      <p class='text-slate-400'>Edit <code class='bg-slate-950 text-rose-400 px-1.5 py-0.5 rounded text-sm font-mono'>src/index.ts</code> to start building your UI.</p>
    </div>
  `;
}""",

    "router": """// ⚡ 自作SPAルーターの基本実装
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

render(window.location.pathname);""",

    "empty": "console.log('Hello TypeScript!');",

    "three": """// Three.js is loaded via CDN in index.html as a global
declare const THREE: any;

const scene    = new THREE.Scene();
const camera   = new THREE.PerspectiveCamera(75, innerWidth / innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(devicePixelRatio);
renderer.setClearColor(0x0f172a);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(1.2, 1.2, 1.2);
const material = new THREE.MeshNormalMaterial();
const cube     = new THREE.Mesh(geometry, material);
scene.add(cube);
camera.position.z = 3;

window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

(function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.008;
  cube.rotation.y += 0.012;
  renderer.render(scene, camera);
})();""",

    "alpine": """// Alpine.js handles UI reactivity via x-data in index.html.
// Use this file for TypeScript utilities or additional logic.
console.log('Alpine.js + TypeScript ready!');""",

    "bootstrap": """const btn = document.getElementById('counter-btn');
const display = document.getElementById('counter');
let count = 0;

btn?.addEventListener('click', () => {
  count++;
  if (display) display.textContent = String(count);
});""",
}

HOTRELOAD_SCRIPT = """  <script>
    const ws = new WebSocket('ws://' + location.host + '/ws');
    ws.onmessage = (e) => { if(e.data === 'reload') location.reload(); };
  </script>"""

DESTYLE_CDN   = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/destyle.css@3.0.2/destyle.min.css">'
TAILWIND_CDN  = '<script src="https://cdn.tailwindcss.com"></script>'
THREE_CDN     = '<script src="https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.min.js"></script>'
ALPINE_CDN    = '<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>'
BOOTSTRAP_CSS = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">'
BOOTSTRAP_JS  = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'

DEFAULT_STYLES = """  <style>
    body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #0f172a; color: #f8fafc; display: grid; place-items: center; min-height: 100vh; margin: 0; }
    h1 { font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    p { color: #94a3b8; font-size: 1.1rem; }
    code { background: #1e293b; padding: 0.2rem 0.4rem; border-radius: 0.25rem; color: #f43f5e; font-family: monospace; }
  </style>"""


def get_html(mode: str, title: str) -> str:
    if mode == "tailwind":
        head_extra = f"\n  {TAILWIND_CDN}"
        body_attr  = ' class="bg-slate-900 text-slate-100 min-h-screen grid place-items-center font-sans"'
        body_inner = '  <div id="app"></div>'
        pre_module = ""

    elif mode == "router":
        head_extra = f"\n  {TAILWIND_CDN}"
        body_attr  = ' class="bg-slate-900 text-slate-100 min-h-screen font-sans flex flex-col"'
        body_inner = (
            '  <nav class="bg-slate-950 border-b border-slate-800 px-6 py-4 flex gap-6">\n'
            '    <a href="/" class="nav-link text-sky-400 font-bold hover:text-sky-300">\U0001f3e0 Home</a>\n'
            '    <a href="/about" class="nav-link text-slate-400 font-bold hover:text-slate-200">\U0001f4c4 About</a>\n'
            '    <a href="/setting" class="nav-link text-slate-400 font-bold hover:text-slate-200">⚙️ Setting</a>\n'
            '  </nav>\n'
            '  <main id="app" class="flex-1 grid place-items-center p-6"></main>'
        )
        pre_module = ""

    elif mode == "three":
        head_extra = "\n  <style>body{margin:0;overflow:hidden}canvas{display:block}</style>"
        body_attr  = ""
        body_inner = ""
        pre_module = f"  {THREE_CDN}\n"

    elif mode == "alpine":
        head_extra = f"\n  {TAILWIND_CDN}\n  {ALPINE_CDN}"
        body_attr  = ' class="bg-slate-900 text-slate-100 min-h-screen grid place-items-center font-sans"'
        body_inner = (
            '  <div x-data="{ count: 0, show: true }" class="text-center space-y-6">\n'
            '    <h1 class="text-3xl font-bold text-sky-400">Alpine.js Ready</h1>\n'
            '    <div class="flex items-center gap-6 justify-center">\n'
            '      <button @click="count--" class="w-10 h-10 rounded-full bg-slate-700 hover:bg-slate-600 text-xl font-bold">-</button>\n'
            '      <span x-text="count" class="text-4xl font-mono w-16 text-center"></span>\n'
            '      <button @click="count++" class="w-10 h-10 rounded-full bg-sky-600 hover:bg-sky-500 text-xl font-bold">+</button>\n'
            '    </div>\n'
            '    <button @click="show = !show" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm">Toggle</button>\n'
            '    <p x-show="show" x-transition class="text-slate-400">Edit <code class="text-rose-400 font-mono">src/index.ts</code> for TypeScript logic.</p>\n'
            '  </div>'
        )
        pre_module = ""

    elif mode == "bootstrap":
        head_extra = f"\n  {BOOTSTRAP_CSS}"
        body_attr  = ""
        body_inner = (
            '  <div class="container py-5">\n'
            '    <div class="card bg-dark border-secondary text-center">\n'
            '      <div class="card-body py-5">\n'
            '        <h1 class="card-title text-info mb-3">Bootstrap Ready</h1>\n'
            '        <p class="card-text text-secondary">Edit <code>src/index.ts</code> to get started.</p>\n'
            '        <p class="display-4 fw-bold my-3" id="counter">0</p>\n'
            '        <button class="btn btn-primary" id="counter-btn">Count up</button>\n'
            '      </div>\n'
            '    </div>\n'
            '  </div>'
        )
        pre_module = f"  {BOOTSTRAP_JS}\n"

    elif mode == "empty":
        head_extra = ""
        body_attr  = ""
        body_inner = '  <div id="app"></div>'
        pre_module = ""

    else:  # default
        head_extra = f"\n  {DESTYLE_CDN}\n{DEFAULT_STYLES}"
        body_attr  = ""
        body_inner = '  <div id="app"></div>'
        pre_module = ""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>{head_extra}
</head>
<body{body_attr}>
{body_inner}
{pre_module}  <script type="module" src="./dist/index.js"></script>
{HOTRELOAD_SCRIPT}
</body>
</html>"""
