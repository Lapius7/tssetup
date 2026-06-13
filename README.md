# tssetup

PowerShellやCMDから1コマンドで、Bun + TypeScript の高速なフロントエンド開発環境（ホットリロードサーバー内蔵）を初期構築するツールです。

## 🚀 特徴

- **瞬時にプロジェクト開始:** フォルダ作成、`bun init`、`tsconfig.json` の設定、ホットリロードサーバースクリプトの作成を自動で一括実行します。
- **多彩な初期テンプレート:**
  - `default`: Destyle.css を内包したシンプルな構成（ダークモード対応）。
  - `tailwind`: CDN版 Tailwind CSS が即座に使えるレイアウト構成。
  - `router`: ライブラリを使わずに HTML5 History API を利用した、自作の超軽量 SPA ルーティング構成。
  - `empty`: 最少構成（空の TypeScript ファイルとシンプルな HTML）。
- **エディタ連携:** `--code` オプションを付けるだけで、作成したプロジェクトフォルダを VS Code で即座に開きます。
- **自動バージョン確認:** 実行時に最新バージョンを確認し、更新がある場合は通知します。

---

## 🛠️ インストール方法

**pip（推奨）:**

```bash
pip install tssetup
```

> [!NOTE]
>
> - PowerShell・CMD・Windows Terminal どれからでも使えます。
> - 動作には **Python 3.9+** と **Bun** が必要です。

---

## ⚙️ 動作に必要な環境（依存関係）

| ツール | 用途 | インストール |
| :--- | :--- | :--- |
| **Python 3.9+** | tssetup 本体の実行 | [python.org](https://www.python.org/) |
| **Bun** | プロジェクト初期化・TSコンパイル | `powershell -c "irm bun.sh/install.ps1 \| iex"` |
| **VS Code** (任意) | `--code` オプション使用時 | [code.visualstudio.com](https://code.visualstudio.com/) |

---

## ⚡ 使い方と全パラメータ一覧

```bash
tssetup <プロジェクト名> [--mode <モード名>] [--title <タイトル名>] [--code]
```

引数なしで実行するとバージョン情報・開発者情報のインフォ画面が表示されます。

### パラメータ（引数）詳細

| パラメータ | 短縮形 | 型 | 必須 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `project_name` | - | string | **はい** | - | 作成するプロジェクトのフォルダ名 |
| `--mode` | `-m` | string | いいえ | `default` | テンプレートモード（`default` / `tailwind` / `router` / `empty`） |
| `--title` | `-t` | string | いいえ | `"Bun + TS App"` | `<title>` タグに埋め込むテキスト |
| `--code` | `-c` | flag | いいえ | - | セットアップ完了後に VS Code で開く |
| `--version` | `-v` | flag | いいえ | - | バージョンを表示 |
| `--help` | `-h` | flag | いいえ | - | ヘルプを表示 |

---

### コマンド実行例

```bash
# 標準テンプレートで作成
tssetup my-app

# Tailwind CSS 組み込み + VS Code で開く
tssetup my-app --mode tailwind --code

# 自作 SPA ルーター構成
tssetup my-app --mode router --title "マイSPAサイト"

# 最小構成
tssetup my-app --mode empty
```

---

## 📁 作成されるファイル構成

```
my-app/
├── src/
│   └── index.ts        ← エントリポイント（--mode で内容が変わる）
├── dist/               ← tsc が自動生成するJS出力先
├── node_modules/       ← bun install が自動生成
├── index.html          ← フロントエンドのHTML
├── server.ts           ← ホットリロード対応の開発用Webサーバー
├── tsconfig.json       ← TypeScript コンパイラ設定
└── package.json        ← Bun プロジェクト設定
```

プロジェクト作成後は自動的にそのディレクトリへ移動します。そのまま `tsbuild` を実行すれば開発を始められます。

---

## 🔄 アップデート

```bash
pip install --upgrade tssetup
```

---

## ✉️ 問い合わせ先

- **X (旧Twitter):** [@Lapius7](https://x.com/Lapius7)
- **GitHub Issues:** [Lapius7/tssetup/issues](https://github.com/Lapius7/tssetup/issues)

---

## ⚠️ 免責事項

本ソフトウェアの使用によって生じた直接的・間接的な損害について、作者は一切の責任を負いません。自己責任のもとでご使用ください。

---

## 📄 ライセンス & コピーライト

本プロジェクトは [MIT License](https://opensource.org/licenses/MIT) のもとで公開されています。

Copyright (c) 2026 Lapius7
