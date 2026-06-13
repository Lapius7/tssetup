import argparse
import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path
from typing import Optional
from . import __version__
from .templates import TSCONFIG, SERVER_TS, INDEX_TS, get_html

# --- Console setup (Windows: enable ANSI + force UTF-8) ---

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

R = "\033[0m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"

def c(text, color): return f"{color}{text}{R}"


# --- Version check ---

def fetch_remote_version() -> Optional[str]:
    try:
        url = "https://raw.githubusercontent.com/Lapius7/tssetup/main/version.txt"
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return None


# --- Info screen ---

def show_info(remote: Optional[str]):
    print()
    print(c("🎨 tssetup", CYAN) + c(f"  v{__version__}", GRAY))
    print("Bun + TypeScript フロントエンド環境を1コマンドで構築するツール")
    print()
    print(c("開発者  : ", YELLOW) + "Lapius7")
    print(c("X       : ", YELLOW) + "https://x.com/Lapius7")
    print(c("GitHub  : ", YELLOW) + "https://github.com/Lapius7/tssetup")
    print()
    if remote is None:
        print(f"バージョン  : {__version__}  " + c("(バージョン確認失敗)", GRAY))
    elif remote == __version__:
        print(f"バージョン  : {__version__}  " + c("✅ 最新です", GREEN))
    else:
        print(f"バージョン  : {__version__}  " + c(f"⬆ 最新: {remote}", YELLOW))
    print()
    print(c("使い方  : tssetup <プロジェクト名> [--mode <モード>]", GRAY))
    print(c("ヘルプ  : tssetup --help", GRAY))
    print()


# --- Project creation ---

def create_project(name: str, mode: str, title: str, code: bool):
    project_dir = Path(name)

    print()
    print(c("🔨 ", CYAN) + c(name, WHITE) + c(" を構築中...", CYAN))
    print()

    (project_dir / "src").mkdir(parents=True, exist_ok=True)
    (project_dir / "dist").mkdir(parents=True, exist_ok=True)
    print(c("  📁 src/ dist/ フォルダを作成しました", GRAY))

    os.chdir(project_dir)

    subprocess.run(["bun", "init", "-y"], capture_output=True)
    stale = Path("index.ts")
    if stale.exists():
        stale.unlink()
    print("  📦 package.json" + c("   (bun init)", GRAY))

    Path("tsconfig.json").write_text(TSCONFIG, encoding="utf-8")
    print(c("  ✅ tsconfig.json", GREEN))

    Path("server.ts").write_text(SERVER_TS, encoding="utf-8")
    print(c("  ✅ server.ts", GREEN))

    Path("src/index.ts").write_text(INDEX_TS[mode], encoding="utf-8")
    print(c("  ✅ src/index.ts", GREEN))

    Path("index.html").write_text(get_html(mode, title), encoding="utf-8")
    print(c("  ✅ index.html", GREEN))

    print()
    print(c("  ──────────────────────────────────────────", GRAY))
    print("  ✨ " + c(name, CYAN) + c("  セットアップ完了！", GREEN))
    print(c("  ──────────────────────────────────────────", GRAY))
    print()
    print(c(f"  📁 {name}/", YELLOW))
    print("  ├── src/")
    print("  │   └── index.ts")
    print("  ├── dist/               " + c("← tsc が自動生成", GRAY))
    print("  ├── index.html")
    print("  ├── server.ts")
    print("  ├── tsconfig.json")
    print("  └── package.json")
    print()
    print(c(f"  📂 {Path.cwd()}", GRAY))
    print()
    print(c("  🚀 次のステップ:", CYAN))
    print("     " + c("tsbuild", WHITE) + c("    開発サーバーを起動", GRAY))
    print()

    if code and shutil.which("code"):
        subprocess.run(["code", "."])


# --- Entry point ---

def main():
    parser = argparse.ArgumentParser(
        prog="tssetup",
        description="Bun + TypeScript フロントエンド環境を1コマンドで構築するツール",
        add_help=False,
    )
    parser.add_argument("project_name", nargs="?", help="作成するプロジェクトのフォルダ名")
    parser.add_argument("--mode", "-m",
                        choices=["default", "tailwind", "router", "empty"],
                        default="default",
                        help="テンプレートモード (default/tailwind/router/empty)")
    parser.add_argument("--title", "-t", default="Bun + TS App",
                        help="HTMLの <title> タグに埋め込む文字列")
    parser.add_argument("--code", "-c", action="store_true",
                        help="セットアップ完了後に VS Code で開く")
    parser.add_argument("--version", "-v", action="store_true",
                        help="バージョンを表示")
    parser.add_argument("--help", "-h", action="store_true",
                        help="ヘルプを表示")

    args = parser.parse_args()

    if args.version:
        print(f"tssetup v{__version__}")
        return

    remote = fetch_remote_version()

    if remote and remote != __version__:
        print()
        print(c(f"🔄 新しいバージョン ({remote}) があります。pip install --upgrade tssetup で更新できます。", YELLOW))

    if args.help or not args.project_name:
        if not args.project_name:
            show_info(remote)
        if args.help or not args.project_name:
            parser.print_help()
        return

    create_project(args.project_name, args.mode, args.title, args.code)


if __name__ == "__main__":
    main()
