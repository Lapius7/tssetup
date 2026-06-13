import locale
import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path
from typing import Optional
from . import __version__
from .templates import TSCONFIG, SERVER_TS, GITIGNORE, INDEX_TS, get_html


def _setup_console():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_setup_console()

R      = "\033[0m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

def c(text, color): return f"{color}{text}{R}"
def bar():  return c("  " + "─" * 52, GRAY)
def dbar(): return c("  " + "═" * 52, GRAY)

MODES = ["default", "tailwind", "router", "empty", "three", "alpine", "bootstrap"]


# ── i18n ──────────────────────────────────────────────────────────

def _detect_lang(override: Optional[str] = None) -> str:
    if override in ("ja", "en"):
        return override
    env = os.environ.get("TSSETUP_LANG", "")
    if env in ("ja", "en"):
        return env
    try:
        loc = locale.getdefaultlocale()[0] or ""
        return "ja" if loc.startswith("ja") else "en"
    except Exception:
        return "en"


T: dict = {
    "ja": {
        "tagline":    "Bun + TypeScript フロントエンド環境を1コマンドで構築",
        "author":     "開発者",
        "ver_ok":     "✓ 最新です",
        "ver_fail":   "(バージョン確認失敗)",
        "ver_new":    "↑ v{} が利用可能",
        "update":     "  ↑ 新バージョン v{} があります — pip install --upgrade tssetup",
        "guide":      "使い方",
        "help_lbl":   "ヘルプ",
        "usage":      "使い方",
        "usage_cmd":  "tssetup <プロジェクト名> [オプション]",
        "args":       "引数",
        "arg_name":   "作成するプロジェクトのフォルダ名",
        "opts":       "オプション",
        "o_mode":     "テンプレートモード",
        "o_title":    "HTML の <title> タグのテキスト",
        "o_code":     "完了後に VS Code で開く",
        "o_git":      "git init + .gitignore を生成",
        "o_update":   "最新バージョンに更新",
        "o_list":     "テンプレート一覧を表示",
        "o_lang":     "表示言語",
        "o_ver":      "バージョンを表示",
        "o_help":     "このヘルプを表示",
        "templates":  "テンプレート",
        "m_default":  "Destyle.css + ダークモード対応のシンプル構成",
        "m_tailwind": "Tailwind CSS (CDN) 組み込み",
        "m_router":   "HTML5 History API を使った軽量 SPA ルーター",
        "m_empty":    "最小構成（空の TypeScript + シンプルな HTML）",
        "m_three":    "Three.js (CDN) — 3D シーン（回転キューブ）",
        "m_alpine":   "Alpine.js (CDN) — リアクティブ UI デモ",
        "m_bootstrap":"Bootstrap 5 (CDN) — ダークテーマ + カウンター",
        "examples":   "例",
        "building":   "を構築中...",
        "done":       "✨ セットアップ完了！",
        "next":       "次のステップ",
        "updating":   "🔄 tssetup を最新バージョンに更新中...",
        "up_done":    "✓ 更新完了",
        "already_up": "✓ 既に最新です (v{})",
        "s_dirs":     "src/  dist/",
        "s_pkg":      "package.json",
        "s_tsconfig": "tsconfig.json",
        "s_server":   "server.ts",
        "s_server_n": "ホットリロードサーバー",
        "s_ts":       "src/index.ts",
        "s_html":     "index.html",
        "s_git":      ".gitignore + git init",
    },
    "en": {
        "tagline":    "Scaffold a Bun + TypeScript frontend in one command",
        "author":     "Author",
        "ver_ok":     "✓ up to date",
        "ver_fail":   "(version check failed)",
        "ver_new":    "↑ v{} available",
        "update":     "  ↑ New version v{} available — pip install --upgrade tssetup",
        "guide":      "Guide",
        "help_lbl":   "Help",
        "usage":      "Usage",
        "usage_cmd":  "tssetup <project-name> [options]",
        "args":       "Arguments",
        "arg_name":   "Name of the project folder to create",
        "opts":       "Options",
        "o_mode":     "Template mode",
        "o_title":    "Text for the HTML <title> tag",
        "o_code":     "Open in VS Code after setup",
        "o_git":      "Run git init and generate .gitignore",
        "o_update":   "Update to the latest version",
        "o_list":     "List available templates",
        "o_lang":     "Display language",
        "o_ver":      "Show version",
        "o_help":     "Show this help",
        "templates":  "Templates",
        "m_default":  "Destyle.css + dark mode ready simple layout",
        "m_tailwind": "Tailwind CSS (CDN) included",
        "m_router":   "Lightweight SPA with HTML5 History API routing",
        "m_empty":    "Minimal setup (empty TypeScript + simple HTML)",
        "m_three":    "Three.js (CDN) — 3D scene with rotating cube",
        "m_alpine":   "Alpine.js (CDN) — reactive UI demo",
        "m_bootstrap":"Bootstrap 5 (CDN) — dark theme + counter",
        "examples":   "Examples",
        "building":   " — building...",
        "done":       "✨ Setup complete!",
        "next":       "Next steps",
        "updating":   "🔄 Updating tssetup to the latest version...",
        "up_done":    "✓ Update complete",
        "already_up": "✓ Already up to date (v{})",
        "s_dirs":     "src/  dist/",
        "s_pkg":      "package.json",
        "s_tsconfig": "tsconfig.json",
        "s_server":   "server.ts",
        "s_server_n": "hot-reload server",
        "s_ts":       "src/index.ts",
        "s_html":     "index.html",
        "s_git":      ".gitignore + git init",
    },
}


# ── Version check ──────────────────────────────────────────────────

def fetch_remote_version() -> Optional[str]:
    try:
        url = "https://raw.githubusercontent.com/Lapius7/tssetup/main/version.txt"
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return None


def _ver_badge(remote: Optional[str], lang: str) -> str:
    s = T[lang]
    if remote is None:        return c(s["ver_fail"], GRAY)
    if remote == __version__: return c(s["ver_ok"], GREEN)
    return c(s["ver_new"].format(remote), YELLOW)


# ── Info screen ────────────────────────────────────────────────────

def show_info(remote: Optional[str], lang: str):
    s = T[lang]
    print()
    print(dbar())
    print(c("  🎨  tssetup  ", CYAN) + c(f"v{__version__}", WHITE)
          + "    " + _ver_badge(remote, lang))
    print(dbar())
    print(f"\n  {c(s['tagline'], GRAY)}\n")
    W = 10
    print(f"  {c((s['author']+' ').ljust(W), GRAY)}Lapius7")
    print(f"  {c('X'.ljust(W), GRAY)}https://x.com/Lapius7")
    print(f"  {c('GitHub'.ljust(W), GRAY)}https://github.com/Lapius7/tssetup")
    print(f"  {c('PyPI'.ljust(W), GRAY)}https://pypi.org/project/tssetup")
    print()
    print(f"  {c((s['guide']+' ').ljust(W), GRAY)}{s['usage_cmd']}")
    print(f"  {c((s['help_lbl']+' ').ljust(W), GRAY)}tssetup --help")
    print()
    print(dbar())
    print()


# ── Template list ──────────────────────────────────────────────────

def show_templates(lang: str):
    s = T[lang]
    print()
    print(dbar())
    print(c(f"  🎨  tssetup  {s['templates']}", CYAN))
    print(dbar())
    print()
    pairs = [
        ("default",   "m_default"),
        ("tailwind",  "m_tailwind"),
        ("router",    "m_router"),
        ("three",     "m_three"),
        ("alpine",    "m_alpine"),
        ("bootstrap", "m_bootstrap"),
        ("empty",     "m_empty"),
    ]
    for mode, key in pairs:
        print(f"  {c(mode.ljust(14), CYAN)}{c(s[key], WHITE)}")
    print()
    print(c(f"  tssetup my-app --mode <{'モード' if lang=='ja' else 'mode'}>", GRAY))
    print()
    print(dbar())
    print()


# ── Custom help ────────────────────────────────────────────────────

def _opt(flags: str, desc: str, note: str = ""):
    print(f"  {c(flags.ljust(28), CYAN)}{c(desc, WHITE)}{c('  (' + note + ')', GRAY) if note else ''}")

def _section(title: str):
    print(f"\n  {c(title, YELLOW)}")

def show_help(lang: str):
    s = T[lang]
    print()
    print(dbar())
    print(c("  🎨  tssetup  ", CYAN) + c(f"v{__version__}", WHITE))
    print(c(f"  {s['tagline']}", GRAY))
    print(dbar())

    _section(s["usage"])
    print(f"    {c(s['usage_cmd'], WHITE)}")

    _section(s["args"])
    print(f"    {c('project_name'.ljust(20), CYAN)}{c(s['arg_name'], WHITE)}")

    _section(s["opts"])
    _opt("-m, --mode <mode>",   s["o_mode"],   "default")
    _opt("-t, --title <text>",  s["o_title"],  "Bun + TS App")
    _opt("-c, --code",          s["o_code"])
    _opt("-g, --git",           s["o_git"])
    _opt("-u, --update",        s["o_update"])
    _opt("-l, --list",          s["o_list"])
    _opt("    --lang <lang>",   s["o_lang"],   "ja / en")
    _opt("-v, --version",       s["o_ver"])
    _opt("-h, --help",          s["o_help"])

    _section(s["templates"])
    pairs = [
        ("default",   "m_default"),
        ("tailwind",  "m_tailwind"),
        ("router",    "m_router"),
        ("three",     "m_three"),
        ("alpine",    "m_alpine"),
        ("bootstrap", "m_bootstrap"),
        ("empty",     "m_empty"),
    ]
    for mode, key in pairs:
        print(f"    {c(mode.ljust(12), CYAN)}{c(s[key], WHITE)}")

    _section(s["examples"])
    print(f"    {c('tssetup my-app', WHITE)}")
    print(f"    {c('tssetup my-app --mode tailwind --code', WHITE)}")
    print(f"    {c('tssetup my-app --mode three --git', WHITE)}")
    print(f"    {c('tssetup my-app --mode bootstrap --lang en', WHITE)}")
    print(f"    {c('tssetup --list', WHITE)}")
    print(f"    {c('tssetup --update', WHITE)}")

    print()
    print(dbar())
    print()


# ── Project creation ───────────────────────────────────────────────

def _step(label: str, note: str = ""):
    print(f"  {c('✓', GREEN)}  {c(label.ljust(24), WHITE)}{c(note, GRAY)}")


def create_project(name: str, mode: str, title: str, code: bool, git: bool, lang: str):
    s = T[lang]
    project_dir = Path(name)

    print()
    print(bar())
    print(c("  🎨 tssetup  ", CYAN) + c(name, WHITE) + c(s["building"], GRAY))
    print(bar())
    print()

    (project_dir / "src").mkdir(parents=True, exist_ok=True)
    (project_dir / "dist").mkdir(parents=True, exist_ok=True)
    _step(s["s_dirs"])

    os.chdir(project_dir)

    subprocess.run(["bun", "init", "-y"], capture_output=True)
    stale = Path("index.ts")
    if stale.exists():
        stale.unlink()
    _step(s["s_pkg"], "bun init")

    Path("tsconfig.json").write_text(TSCONFIG, encoding="utf-8")
    _step(s["s_tsconfig"])

    Path("server.ts").write_text(SERVER_TS, encoding="utf-8")
    _step(s["s_server"], s["s_server_n"])

    Path("src/index.ts").write_text(INDEX_TS[mode], encoding="utf-8")
    _step(s["s_ts"], f"mode: {mode}")

    Path("index.html").write_text(get_html(mode, title), encoding="utf-8")
    _step(s["s_html"])

    if git:
        subprocess.run(["git", "init"], capture_output=True)
        Path(".gitignore").write_text(GITIGNORE, encoding="utf-8")
        _step(s["s_git"])

    print()
    print(bar())
    print(c(f"  {s['done']}", GREEN))
    print(bar())
    print()
    print(c(f"  {name}/", YELLOW))
    print(f"  ├── {c('src/index.ts', WHITE)}")
    print(f"  ├── {c('dist/', GRAY)}")
    print(f"  ├── {c('index.html', WHITE)}")
    print(f"  ├── {c('server.ts', WHITE)}")
    print(f"  ├── {c('tsconfig.json', WHITE)}")
    print(f"  └── {c('package.json', WHITE)}")
    if git:
        print(f"  └── {c('.gitignore', WHITE)}")
    print()
    print(c(f"  {s['next']}:", CYAN))
    print(f"    {c('cd ./' + name, WHITE)}")
    print(f"    {c('tsbuild', WHITE)}")
    print()

    if code and shutil.which("code"):
        subprocess.run(["code", "."])


# ── Self-update ────────────────────────────────────────────────────

def do_update(remote: Optional[str], lang: str):
    s = T[lang]
    if remote and remote == __version__:
        print(c(s["already_up"].format(__version__), GREEN))
        return
    print(c(s["updating"], CYAN))
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "tssetup"])
    print(c(s["up_done"], GREEN))


# ── Entry point ────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(prog="tssetup", add_help=False)
    parser.add_argument("project_name", nargs="?")
    parser.add_argument("--mode",    "-m", choices=MODES, default="default")
    parser.add_argument("--title",   "-t", default="Bun + TS App")
    parser.add_argument("--code",    "-c", action="store_true")
    parser.add_argument("--git",     "-g", action="store_true")
    parser.add_argument("--update",  "-u", action="store_true")
    parser.add_argument("--list",    "-l", action="store_true")
    parser.add_argument("--lang",          default=None)
    parser.add_argument("--version", "-v", action="store_true")
    parser.add_argument("--help",    "-h", action="store_true")

    args = parser.parse_args()
    lang = _detect_lang(args.lang)

    if args.version:
        print(f"tssetup v{__version__}")
        return

    remote = fetch_remote_version()

    if remote and remote != __version__:
        print()
        print(c(T[lang]["update"].format(remote), YELLOW))

    if args.update:
        do_update(remote, lang)
        return

    if args.list:
        show_templates(lang)
        return

    if args.help:
        show_help(lang)
        return

    if not args.project_name:
        show_info(remote, lang)
        return

    create_project(args.project_name, args.mode, args.title, args.code, args.git, lang)


if __name__ == "__main__":
    main()
