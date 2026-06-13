import itertools
import locale
import os
import re
import sys
import subprocess
import shutil
import threading
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator
from . import __version__
from .templates import TSCONFIG, SERVER_TS, INDEX_TS, get_html


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

R    = "\033[0m"
CYAN = "\033[36m"
BCYN = "\033[1;96m"  # Bold Bright Cyan
GREEN= "\033[32m"
BGRE = "\033[1;32m"  # Bold Green
YEL  = "\033[33m"
WHITE= "\033[97m"
BWHT = "\033[1;97m"  # Bold White
GRAY = "\033[90m"
RED  = "\033[31m"

def c(text, color): return f"{color}{text}{R}"
def bar():  return c("  " + "─" * 52, GRAY)
def dbar(): return c("  " + "═" * 52, GRAY)

MODES = ["default", "tailwind", "router", "three", "alpine", "bootstrap", "empty"]

IS_TTY = sys.stdout.isatty()

FILE_ICONS = {
    "src":          "📂",
    "dist":         "📁",
    "index.ts":     "📄",
    "index.html":   "🌐",
    "server.ts":    "⚡",
    "tsconfig.json":"🔧",
    "package.json": "📦",
}


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
        "tagline":     "Bun + TypeScript フロントエンド環境を1コマンドで構築",
        "author":      "開発者",
        "ver_ok":      "✓ 最新です",
        "ver_fail":    "(バージョン確認失敗)",
        "ver_new":     "↑ v{} が利用可能",
        "update":      "  ↑ 新バージョン v{} があります — pip install --upgrade tssetup",
        "guide":       "使い方",
        "help_lbl":    "ヘルプ",
        "usage":       "使い方",
        "usage_cmd":   "tssetup <プロジェクト名> [オプション]",
        "args":        "引数",
        "arg_name":    "作成するプロジェクトのフォルダ名（. で現在のフォルダに生成）",
        "opts":        "オプション",
        "o_mode":      "テンプレートモード",
        "o_title":     "HTML の <title> タグのテキスト",
        "o_code":      "完了後に VS Code で開く",
        "o_open":      "完了後にエクスプローラーで開く",
        "o_update":    "最新バージョンに更新",
        "o_list":      "テンプレート一覧を表示",
        "o_interactive":"対話形式でプロジェクトを設定",
        "o_lang":      "表示言語",
        "o_ver":       "バージョンを表示",
        "o_help":      "このヘルプを表示",
        "templates":   "テンプレート",
        "m_default":   "Destyle.css + ダークモード対応のシンプル構成",
        "m_tailwind":  "Tailwind CSS (CDN) 組み込み",
        "m_router":    "HTML5 History API を使った軽量 SPA ルーター",
        "m_three":     "Three.js (CDN) — 3D シーン（回転キューブ）",
        "m_alpine":    "Alpine.js (CDN) — リアクティブ UI デモ",
        "m_bootstrap": "Bootstrap 5 (CDN) — ダークテーマ + カウンター",
        "m_empty":     "最小構成（空の TypeScript + シンプルな HTML）",
        "examples":    "例",
        "no_bun":      "Bun がインストールされていません",
        "bun_install": "インストール: powershell -c \"irm bun.sh/install.ps1 | iex\"",
        "name_bad":    "使えない文字が含まれています",
        "name_exists": "は既に存在します",
        "i_name":      "プロジェクト名",
        "i_default":   "デフォルト",
        "i_template":  "テンプレートを選択 (番号)",
        "i_title":     "ページタイトル",
        "i_code":      "VS Code で開く? (y/N)",
        "building":    "─ セットアップ中...",
        "done":        "✨  セットアップ完了！",
        "next":        "次のステップ",
        "updating":    "🔄 tssetup を最新バージョンに更新中...",
        "up_done":     "✓ 更新完了",
        "already_up":  "✓ 既に最新です (v{})",
        "s_dirs":      "📂 src/  📁 dist/",
        "s_pkg":       "📦 package.json",
        "s_tsconfig":  "🔧 tsconfig.json",
        "s_server":    "⚡ server.ts",
        "s_server_n":  "ホットリロードサーバー",
        "s_ts":        "📄 src/index.ts",
        "s_html":      "🌐 index.html",
    },
    "en": {
        "tagline":     "Scaffold a Bun + TypeScript frontend in one command",
        "author":      "Author",
        "ver_ok":      "✓ up to date",
        "ver_fail":    "(version check failed)",
        "ver_new":     "↑ v{} available",
        "update":      "  ↑ New version v{} available — pip install --upgrade tssetup",
        "guide":       "Guide",
        "help_lbl":    "Help",
        "usage":       "Usage",
        "usage_cmd":   "tssetup <project-name> [options]",
        "args":        "Arguments",
        "arg_name":    "Project folder name (use . to scaffold in current directory)",
        "opts":        "Options",
        "o_mode":      "Template mode",
        "o_title":     "Text for the HTML <title> tag",
        "o_code":      "Open in VS Code after setup",
        "o_open":      "Open in Explorer after setup",
        "o_update":    "Update to the latest version",
        "o_list":      "List available templates",
        "o_interactive":"Interactive project setup",
        "o_lang":      "Display language",
        "o_ver":       "Show version",
        "o_help":      "Show this help",
        "templates":   "Templates",
        "m_default":   "Destyle.css + dark mode ready simple layout",
        "m_tailwind":  "Tailwind CSS (CDN) included",
        "m_router":    "Lightweight SPA with HTML5 History API routing",
        "m_three":     "Three.js (CDN) — 3D scene with rotating cube",
        "m_alpine":    "Alpine.js (CDN) — reactive UI demo",
        "m_bootstrap": "Bootstrap 5 (CDN) — dark theme + counter",
        "m_empty":     "Minimal setup (empty TypeScript + simple HTML)",
        "examples":    "Examples",
        "no_bun":      "Bun is not installed",
        "bun_install": "Install: powershell -c \"irm bun.sh/install.ps1 | iex\"",
        "name_bad":    "Invalid characters in project name",
        "name_exists": "already exists",
        "i_name":      "Project name",
        "i_default":   "default",
        "i_template":  "Select template (number)",
        "i_title":     "Page title",
        "i_code":      "Open in VS Code? (y/N)",
        "building":    "─ building...",
        "done":        "✨  Setup complete!",
        "next":        "Next steps",
        "updating":    "🔄 Updating tssetup to the latest version...",
        "up_done":     "✓ Update complete",
        "already_up":  "✓ Already up to date (v{})",
        "s_dirs":      "📂 src/  📁 dist/",
        "s_pkg":       "📦 package.json",
        "s_tsconfig":  "🔧 tsconfig.json",
        "s_server":    "⚡ server.ts",
        "s_server_n":  "hot-reload server",
        "s_ts":        "📄 src/index.ts",
        "s_html":      "🌐 index.html",
    },
}


# ── Spinner ────────────────────────────────────────────────────────

@contextmanager
def spinning(label: str, note: str = "") -> Generator:
    if not IS_TTY:
        yield
        _step(label, note)
        return
    stop = threading.Event()
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    def _spin():
        for f in itertools.cycle(frames):
            if stop.is_set():
                break
            print(f"\r  {c(f, CYAN)}  {c(label, GRAY)}", end="", flush=True)
            time.sleep(0.08)

    t = threading.Thread(target=_spin, daemon=True)
    t.start()
    try:
        yield
    finally:
        stop.set()
        t.join()
        _step(label, note)


def _step(label: str, note: str = ""):
    n = c(f"  {note}", GRAY) if note else ""
    print(f"\r  {c('✓', GREEN)}  {c(label.ljust(26), WHITE)}{n}", flush=True)


# ── Checks ─────────────────────────────────────────────────────────

def check_bun(lang: str):
    if not shutil.which("bun"):
        s = T[lang]
        print()
        print(c(f"  ✗  {s['no_bun']}", RED))
        print(c(f"  {s['bun_install']}", YEL))
        print()
        sys.exit(1)


def validate_name(name: str, lang: str) -> Optional[str]:
    if name == ".":
        return None
    s = T[lang]
    if re.search(r'[<>:"/\\|?*\s]', name):
        bad = "".join(sorted(set(re.findall(r'[<>:"/\\|?*\s]', name))))
        return f"  ✗  {s['name_bad']}: {c(repr(bad), YEL)}"
    if Path(name).exists():
        return f"  ✗  {c(name, WHITE)} {s['name_exists']}"
    return None


# ── Version ────────────────────────────────────────────────────────

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
    return c(s["ver_new"].format(remote), YEL)


def _logo():
    return c("ts", BCYN) + c("setup", CYAN)


# ── Info screen ────────────────────────────────────────────────────

def show_info(remote: Optional[str], lang: str):
    s = T[lang]
    print()
    print(dbar())
    print(f"  🎨  {_logo()}  {c(f'v{__version__}', GRAY)}    {_ver_badge(remote, lang)}")
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
    pairs = [("default","m_default"),("tailwind","m_tailwind"),("router","m_router"),
             ("three","m_three"),("alpine","m_alpine"),("bootstrap","m_bootstrap"),("empty","m_empty")]
    print()
    print(dbar())
    print(f"  🎨  {_logo()}  {c(s['templates'], GRAY)}")
    print(dbar())
    print()
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
    print(f"\n  {c(title, YEL)}")

def show_help(lang: str):
    s = T[lang]
    print()
    print(dbar())
    print(f"  🎨  {_logo()}  {c(f'v{__version__}', GRAY)}")
    print(c(f"  {s['tagline']}", GRAY))
    print(dbar())

    _section(s["usage"])
    print(f"    {c(s['usage_cmd'], WHITE)}")

    _section(s["args"])
    print(f"    {c('project_name'.ljust(18), CYAN)}{c(s['arg_name'], WHITE)}")

    _section(s["opts"])
    _opt("-m, --mode <mode>",   s["o_mode"],        "default")
    _opt("-t, --title <text>",  s["o_title"],        "Bun + TS App")
    _opt("-c, --code",          s["o_code"])
    _opt("-o, --open",          s["o_open"])
    _opt("-i, --interactive",   s["o_interactive"])
    _opt("-u, --update",        s["o_update"])
    _opt("-l, --list",          s["o_list"])
    _opt("    --lang <lang>",   s["o_lang"],         "ja / en")
    _opt("-v, --version",       s["o_ver"])
    _opt("-h, --help",          s["o_help"])

    _section(s["templates"])
    pairs = [("default","m_default"),("tailwind","m_tailwind"),("router","m_router"),
             ("three","m_three"),("alpine","m_alpine"),("bootstrap","m_bootstrap"),("empty","m_empty")]
    for mode, key in pairs:
        print(f"    {c(mode.ljust(12), CYAN)}{c(s[key], WHITE)}")

    _section(s["examples"])
    print(f"    {c('tssetup my-app', WHITE)}")
    print(f"    {c('tssetup .', WHITE)}                          {c('# ' + ('現在のフォルダに生成' if lang=='ja' else 'scaffold here'), GRAY)}")
    print(f"    {c('tssetup my-app --mode tailwind --code', WHITE)}")
    print(f"    {c('tssetup my-app --mode three --open', WHITE)}")
    print(f"    {c('tssetup -i', WHITE)}                         {c('# ' + ('対話形式' if lang=='ja' else 'interactive'), GRAY)}")
    print(f"    {c('tssetup --list', WHITE)}")
    print(f"    {c('tssetup --update', WHITE)}")
    print()
    print(dbar())
    print()


# ── Interactive mode ───────────────────────────────────────────────

def interactive_setup(lang: str) -> tuple:
    s = T[lang]
    pairs = [("default","m_default"),("tailwind","m_tailwind"),("router","m_router"),
             ("three","m_three"),("alpine","m_alpine"),("bootstrap","m_bootstrap"),("empty","m_empty")]
    print()
    print(dbar())
    print(f"  🎨  {_logo()}  {c('interactive', YEL)}")
    print(dbar())
    print()

    name = input(f"  {c(s['i_name'], YEL)} › ").strip() or "my-app"
    print()

    for i, (mode, key) in enumerate(pairs, 1):
        print(f"    {c(str(i), GRAY)}  {c(mode.ljust(12), CYAN)}{c(s[key], GRAY)}")
    print()

    raw = input(f"  {c(s['i_template'], YEL)} [{c('1', WHITE)}] › ").strip()
    try:
        mode = pairs[int(raw) - 1][0]
    except (ValueError, IndexError):
        mode = "default"

    title = input(f"  {c(s['i_title'], YEL)} [{c('Bun + TS App', WHITE)}] › ").strip() or "Bun + TS App"
    code_raw = input(f"  {c(s['i_code'], YEL)} › ").strip().lower()
    code = code_raw in ("y", "yes")

    print()
    return name, mode, title, code


# ── Project creation ───────────────────────────────────────────────

def create_project(name: str, mode: str, title: str, code: bool, open_dir: bool, lang: str):
    s = T[lang]
    in_place = (name == ".")
    project_dir = Path(".") if in_place else Path(name)
    display_name = Path.cwd().name if in_place else name

    print()
    print(bar())
    print(f"  🎨  {_logo()}  {c(display_name, BWHT)}  {c(s['building'], GRAY)}")
    print(bar())
    print()

    (project_dir / "src").mkdir(parents=True, exist_ok=True)
    (project_dir / "dist").mkdir(parents=True, exist_ok=True)
    _step(s["s_dirs"])

    if not in_place:
        os.chdir(project_dir)

    with spinning(s["s_pkg"], "bun init"):
        subprocess.run(["bun", "init", "-y"], capture_output=True)
        stale = Path("index.ts")
        if stale.exists():
            stale.unlink()

    Path("tsconfig.json").write_text(TSCONFIG, encoding="utf-8")
    _step(s["s_tsconfig"])

    Path("server.ts").write_text(SERVER_TS, encoding="utf-8")
    _step(s["s_server"], s["s_server_n"])

    Path("src/index.ts").write_text(INDEX_TS[mode], encoding="utf-8")
    _step(s["s_ts"], f"mode: {mode}")

    Path("index.html").write_text(get_html(mode, title), encoding="utf-8")
    _step(s["s_html"])

    print()
    print(bar())
    print(c(f"  {s['done']}", BGRE))
    print(bar())
    print()
    print(c(f"  {display_name}/", YEL))
    print(f"  ├── {c('📂 src/', CYAN)}")
    print(f"  │   └── {c('📄 index.ts', WHITE)}")
    print(f"  ├── {c('📁 dist/', GRAY)}")
    print(f"  ├── {c('🌐 index.html', WHITE)}")
    print(f"  ├── {c('⚡ server.ts', WHITE)}")
    print(f"  ├── {c('🔧 tsconfig.json', WHITE)}")
    print(f"  └── {c('📦 package.json', WHITE)}")
    print()
    print(c(f"  {s['next']}:", CYAN))
    if not in_place:
        print(f"    {c('cd ./' + display_name, WHITE)}")
    print(f"    {c('tsbuild', WHITE)}")
    print()

    if code and shutil.which("code"):
        subprocess.run(["code", "."])
    if open_dir:
        subprocess.Popen(["explorer", str(Path.cwd())])


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
    parser.add_argument("--mode",        "-m", choices=MODES, default="default")
    parser.add_argument("--title",       "-t", default="Bun + TS App")
    parser.add_argument("--code",        "-c", action="store_true")
    parser.add_argument("--open",        "-o", action="store_true")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--update",      "-u", action="store_true")
    parser.add_argument("--list",        "-l", action="store_true")
    parser.add_argument("--lang",              default=None)
    parser.add_argument("--version",     "-v", action="store_true")
    parser.add_argument("--help",        "-h", action="store_true")

    args = parser.parse_args()
    lang = _detect_lang(args.lang)

    if args.version:
        print(f"tssetup v{__version__}")
        return

    remote = fetch_remote_version()

    if remote and remote != __version__:
        print()
        print(c(T[lang]["update"].format(remote), YEL))

    if args.update:
        do_update(remote, lang)
        return

    if args.list:
        show_templates(lang)
        return

    if args.help:
        show_help(lang)
        return

    if args.interactive:
        name, mode, title, code = interactive_setup(lang)
    elif args.project_name:
        name, mode, title, code = args.project_name, args.mode, args.title, args.code
    else:
        show_info(remote, lang)
        return

    err = validate_name(name, lang)
    if err:
        print(c(err, RED))
        return

    check_bun(lang)
    create_project(name, mode, title, code, args.open, lang)


if __name__ == "__main__":
    main()
