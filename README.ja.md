<div align="center">

<p align="center"><a href="README.md">English</a> | <b>日本語</b></p>

<h1 align="center">tssetup</h1>

<h3 align="center">Bun + TypeScript のフロントエンド環境を 1 コマンドで作ります。</h3>

<p align="center">PowerShell や CMD から、ホットリロード付きの開発サーバーを備えた Bun + TypeScript のプロジェクトを作ります。起動には <a href="https://github.com/Lapius7/tsbuild">tsbuild</a> と組み合わせます。</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@lapius/tssetup"><img alt="npm" src="https://img.shields.io/npm/v/@lapius/tssetup?style=flat-square&color=cb3837&logo=npm"></a>
  <a href="https://pypi.org/project/tssetup/"><img alt="PyPI" src="https://img.shields.io/pypi/v/tssetup?style=flat-square&color=3775a9&logo=pypi&logoColor=white"></a>
  <a href="https://bun.sh"><img alt="Bun" src="https://img.shields.io/badge/runtime-Bun-fbf0df?logo=bun&logoColor=000000&style=flat-square&labelColor=000000"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/Lapius7/tssetup?style=flat-square&color=97ca00"></a>
  <a href="https://github.com/Lapius7/tssetup/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/Lapius7/tssetup?style=flat-square&color=e3b341&logo=github"></a>
  <a href="https://github.com/Lapius7/tssetup/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/Lapius7/tssetup?style=flat-square&color=3b82f6"></a>
</p>

<p align="center"><a href="#最短セットアップ">最短セットアップ</a> · <a href="#オプション">オプション</a> · <a href="#テンプレート">テンプレート</a> · <a href="#アップデート">アップデート</a></p>

</div>

---

## 特長

- **すぐ始められる**: フォルダの作成、`bun init`、`tsconfig.json` の設定、ホットリロード用サーバースクリプトの作成をまとめて行います。
- **テンプレート**: `default`、`tailwind`、`router`、`three`、`alpine`、`bootstrap`、`empty` から選べます（[テンプレート](#テンプレート)）。
- **エディタで開く**: `--code` で VS Code、`--open` でエクスプローラーを開きます。
- **対話モード**: `-i` で設定を順に聞かれます。
- **更新の確認**: 新しい版があれば知らせます。

## 最短セットアップ

**Python 3.9 以上**と **Bun** が要ります。VS Code は `--code` を使うときだけ要ります。

```sh
pnpm add -g @lapius/tssetup
# または
pip install tssetup
```

> [!NOTE]
> npm 版は pnpm 前提です。npm と pnpm の両方に入れると同じコマンドが二重になるので、`pnpm add -g` だけを使ってください。npm 版は Python 版を起動する入口なので、Node.js 18 以上も要ります。

```sh
tssetup my-app                        # 標準のテンプレート
tssetup my-app --mode tailwind --code # Tailwind CSS で作り、VS Code で開く
tssetup my-app --mode router --title "マイSPAサイト"
tssetup my-app --mode empty           # 最小構成
tssetup .                             # カレントディレクトリに作る
tssetup -i                            # 対話形式
```

作成後はそのプロジェクトのディレクトリへ移動します。そこで [`tsbuild`](https://github.com/Lapius7/tsbuild) を実行すれば、開発を始められます。引数なしで実行すると、バージョンとインフォ画面を表示します。

| ツール | 用途 | インストール |
|---|---|---|
| Python 3.9+ | tssetup 本体の実行 | [python.org](https://www.python.org/) |
| Bun | プロジェクトの初期化と TypeScript のコンパイル | `powershell -c "irm bun.sh/install.ps1 \| iex"` |
| VS Code（任意） | `--code` | [code.visualstudio.com](https://code.visualstudio.com/) |

## オプション

```sh
tssetup <プロジェクト名> [--mode <モード名>] [--title <タイトル名>] [--code]
```

| オプション | 短縮形 | 既定値 | 内容 |
|---|---|---|---|
| `project_name` | | 必須 | プロジェクトのフォルダ名（`.` で現在のディレクトリ） |
| `--mode <mode>` | `-m` | `default` | テンプレートモード |
| `--title <text>` | `-t` | `Bun + TS App` | HTML の `<title>` に入れる文字 |
| `--code` | `-c` | | 作成後に VS Code で開く |
| `--open` | `-o` | | 作成後にエクスプローラーで開く |
| `--interactive` | `-i` | | 対話形式で設定する |
| `--list` | `-l` | | テンプレートの一覧を表示 |
| `--update` | `-u` | | 最新版に更新 |
| `--lang <lang>` | | | 表示言語（`ja` / `en`） |
| `--version` | `-v` | | バージョンを表示 |
| `--help` | `-h` | | ヘルプを表示 |

## テンプレート

| モード | 内容 |
|---|---|
| `default` | Destyle.css を使った、ダークモード対応のシンプルな構成 |
| `tailwind` | CDN 版の Tailwind CSS をすぐ使える構成 |
| `router` | ライブラリなしで、HTML5 History API を使った小さな SPA ルーター |
| `three` | Three.js（CDN）で立方体を回す構成 |
| `alpine` | Alpine.js（CDN）のリアクティブ UI のデモ |
| `bootstrap` | Bootstrap 5（CDN）のダークテーマとカウンター |
| `empty` | 空の TypeScript ファイルとシンプルな HTML |

## 作成されるファイル

```
my-app/
├── src/
│   └── index.ts        ← エントリポイント（--mode で内容が変わる）
├── dist/               ← tsc の出力先
├── node_modules/       ← bun install が作る
├── index.html          ← フロントエンドの HTML
├── server.ts           ← ホットリロード対応の開発用サーバー
├── tsconfig.json       ← TypeScript の設定
└── package.json        ← Bun プロジェクトの設定
```

## アップデート

```sh
tssetup --update
```

再インストールでも更新できます。`pnpm add -g @lapius/tssetup` / `pip install --upgrade tssetup`

## 安全のために

> [!NOTE]
> 既存の README と PyPI の記載は Windows（PowerShell、CMD、Windows Terminal）向けです。Linux と macOS での動作は、この README の作成時には確認していません。`three`、`alpine`、`bootstrap` は旧 README になかったテンプレートで、コードとヘルプ表示で確かめただけです。実際に生成して動かしてはいません。

本ソフトウェアの使用で生じた損害について、作者は責任を負いません。自己責任で使ってください。

## 問い合わせ

- X: [@Lapius7](https://x.com/Lapius7)
- [GitHub Issues](https://github.com/Lapius7/tssetup/issues)

## ライセンス

[MIT](LICENSE) © 2026 Lapius7
