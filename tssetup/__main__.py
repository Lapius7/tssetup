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
def bar(): return c("  " + "─" * 44, GRAY)


def fetch_remote_version() -> Optional[str]:
    try:
        url = "https://raw.githubusercontent.com/Lapius7/tssetup/main/version.txt"
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return None


def show_info(remote: Optional[str]):
    if remote is None:
        status = c("(バージョン確認失敗)", GRAY)
    elif remote == __version__:
        status = c("✓ 最新です", GREEN)
    else:
        status = c(f"↑ v{remote} が利用可能", YELLOW)

    print()
    print(c("  tssetup", CYAN) + c(f" v{__version__}  ", GRAY) + status)
    print(c("  Bun + TypeScript フロントエンド環境を1コマンドで構築", GRAY))
    print()
    print(c("  開発者  ", GRAY) + "Lapius7")
    print(c("  X       ", GRAY) + "https://x.com/Lapius7")
    print(c("  GitHub  ", GRAY) + "https://github.com/Lapius7/tssetup")
    print()
    print(c("  使い方  tssetup <プロジェクト名> [--mode <モード>]", GRAY))
    print(c("  ヘルプ  tssetup --help", GRAY))
    print()


def _step(label: str, note: str = ""):
    label_col = c(label.ljust(20), WHITE)
    note_col  = c(note, GRAY) if note else ""
    print(f"  {c('✓', GREEN)}  {label_col}{note_col}")


def create_project(name: str, mode: str, title: str, code: bool):
    project_dir = Path(name)

    print()
    print(bar())
    print(c("  🎨 tssetup  ", CYAN) + c(name, WHITE))
    print(bar())
    print()

    (project_dir / "src").mkdir(parents=True, exist_ok=True)
    (project_dir / "dist").mkdir(parents=True, exist_ok=True)
    _step("src/  dist/")

    os.chdir(project_dir)

    subprocess.run(["bun", "init", "-y"], capture_output=True)
    stale = Path("index.ts")
    if stale.exists():
        stale.unlink()
    _step("package.json", "bun init")

    Path("tsconfig.json").write_text(TSCONFIG, encoding="utf-8")
    _step("tsconfig.json")

    Path("server.ts").write_text(SERVER_TS, encoding="utf-8")
    _step("server.ts", "ホットリロードサーバー")

    Path("src/index.ts").write_text(INDEX_TS[mode], encoding="utf-8")
    _step("src/index.ts", f"mode: {mode}")

    Path("index.html").write_text(get_html(mode, title), encoding="utf-8")
    _step("index.html")

    print()
    print(bar())
    print(c("  ✨ セットアップ完了！", GREEN))
    print(bar())
    print()
    print(c(f"  {name}/", YELLOW))
    print(f"  ├── {c('src/index.ts', WHITE)}")
    print(f"  ├── {c('dist/', GRAY)}")
    print(f"  ├── {c('index.html', WHITE)}")
    print(f"  ├── {c('server.ts', WHITE)}")
    print(f"  ├── {c('tsconfig.json', WHITE)}")
    print(f"  └── {c('package.json', WHITE)}")
    print()
    print(c("  次のステップ:", CYAN))
    print(f"    {c('cd ./' + name, WHITE)}")
    print(f"    {c('tsbuild', WHITE)}")
    print()

    if code and shutil.which("code"):
        subprocess.run(["code", "."])


def main():
    parser = argparse.ArgumentParser(
        prog="tssetup",
        description="Bun + TypeScript フロントエンド環境を1コマンドで構築するツール",
        add_help=False,
    )
    parser.add_argument("project_name", nargs="?")
    parser.add_argument("--mode", "-m",
                        choices=["default", "tailwind", "router", "empty"],
                        default="default")
    parser.add_argument("--title", "-t", default="Bun + TS App")
    parser.add_argument("--code", "-c", action="store_true")
    parser.add_argument("--version", "-v", action="store_true")
    parser.add_argument("--help", "-h", action="store_true")

    args = parser.parse_args()

    if args.version:
        print(f"tssetup v{__version__}")
        return

    remote = fetch_remote_version()

    if remote and remote != __version__:
        print()
        print(c(f"  ↑ 新バージョン v{remote} があります  pip install --upgrade tssetup", YELLOW))

    if args.help or not args.project_name:
        show_info(remote)
        if args.help:
            parser.print_help()
        return

    create_project(args.project_name, args.mode, args.title, args.code)


if __name__ == "__main__":
    main()
