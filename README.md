# tssetup

PowerShellから1コマンドで、Bun + TypeScript の高速なフロントエンド開発環境（ホットリロードサーバー内蔵）を初期構築するツールです。

## 🚀 特徴

*   **瞬時にプロジェクト開始:** フォルダ作成、`bun init`、`tsconfig.json` の設定、ホットリロードサーバースクリプトの作成を自動で一括実行します。
*   **多彩な初期テンプレート:**
    *   `default`: Destyle.cssを内包したシンプルな構成（ダークモード対応）。
    *   `tailwind`: CDN版Tailwind CSSが即座に使えるレイアウト構成。
    *   `router`: ライブラリを使わずにHTML5 History APIを利用した、自作の超軽量SPAルーティング構成。
    *   `empty`: 最少構成（空のTypeScriptファイルとシンプルなHTML）。
*   **エディタ連携:** `-Code` オプションを付けるだけで、作成したプロジェクトフォルダをVS Codeで即座に開きます。
*   **自動バージョン更新:** 実行時に最新バージョンを自動確認し、新しいバージョンがあれば自動で更新します。
*   **安全なアンインストール:** `-Uninstall` オプションで確認プロンプト付きの安全なアンインストールができます。

---

## 🛠️ インストール方法

PowerShellで以下のコマンドを実行するだけで、お使いの環境（`$PROFILE`）に `tssetup` コマンドがインストールされます。

```powershell
irm https://raw.githubusercontent.com/Lapius7/tssetup/main/install.ps1 | iex
```

> [!NOTE]
>
> - インストール完了後、現在のPowerShellセッションに反映するには `. $PROFILE` を実行するか、新しくPowerShellを開き直してください。
> - インストーラーは既存の `$PROFILE` を安全に保持したまま `tssetup` 関数のブロックのみを追記します。既存のユーザー設定は上書きされません。

---

## ⚙️ 動作に必要な環境（依存関係）

このコマンドを動かすには、システムに以下のツールがあらかじめインストールされている必要があります。

1.  **PowerShell 5.1 以上** (Windows標準)
2.  **Bun** (高速JavaScriptランタイム)
    *   インストールされていない場合は、PowerShellで以下を実行します：
        ```powershell
        powershell -c "irm bun.sh/install.ps1 | iex"
        ```
3.  **TypeScript** (トランスパイラ)
    *   Bun経由で自動的に実行されるためグローバルインストールは必須ではありませんが、コマンド内部で `bun x tsc` を呼び出します。
4.  **VS Code (Visual Studio Code)** (任意)
    *   `-Code` オプションを使用する場合に必要です（環境変数 `Path` に `code` コマンドが登録されている必要があります）。

---

## ⚡ 使い方と全パラメータ一覧

```powershell
tssetup <プロジェクト名> [-Mode <モード名>] [-Title <タイトル名>] [-Code] [-Help]
```

引数なしで実行するとバージョン情報・開発者情報のインフォ画面が表示されます。

### パラメータ（引数）詳細

| パラメータ名 | エイリアス | 型 | 必須 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ProjectName`** | (位置引数 `0`) | `string` | **はい** | - | 作成するプロジェクトのフォルダ名。相対パス・絶対パスが指定可能です。 |
| **`-Mode`** | `-m` | `string` | いいえ | `default` | テンプレートの初期構造。`default`, `tailwind`, `router`, `empty` から選択。 |
| **`-Title`** | `-t` | `string` | いいえ | `"Bun + TS App"` | 生成される `index.html` の `<title>` タグに埋め込まれるテキスト。 |
| **`-Code`** | `-c` | `switch` | いいえ | `$false` | 指定すると、セットアップ完了直後に自動で VS Code でプロジェクトを開きます。 |
| **`-Help`** | `-h` | `switch` | いいえ | `$false` | コマンドのヘルプメッセージ（使い方とオプション）を表示して終了します。 |
| **`-Uninstall`** | - | `switch` | いいえ | `$false` | 確認プロンプトの後、`$PROFILE` から `tssetup` を削除してアンインストールします。 |

---

### コマンド実行例（ユースケース別）

#### 1. 最もシンプルな基本構成で作成する
```powershell
tssetup my-app
```
`my-app` フォルダがカレントディレクトリ配下に作成され、自動的に `bun init` や `tsconfig.json` が配置されます。作成後はそのフォルダへ自動で移動します。

#### 2. Tailwind CSS が即座に使える状態でセットアップし、そのまま VS Code で開く
```powershell
tssetup tailwind-project -Mode tailwind -Code
```

#### 3. HTMLの `<title>` をカスタマイズし、最少の空テンプレートで開始する
```powershell
tssetup empty-app -Mode empty -Title "最小のデモアプリ"
```

#### 4. ルーティング（SPA）構成を準備し、VS Code で開く
```powershell
tssetup spa-demo -Mode router -Title "マイSPAサイト" -Code
```
このモードでは、ライブラリ無しの状態で「Home」「About」「Setting」のページ切り替え機能が最初から動作します。

#### 5. ヘルプを表示する
```powershell
tssetup -Help
```

---

## 📁 作成されるファイル構成

`tssetup myapp` を実行すると、以下の構成でプロジェクトフォルダが生成されます。

```
myapp/
├── src/
│   └── index.ts        ← エントリポイント（-Mode オプションで内容が変わる）
├── dist/               ← コンパイル後のJS（tsc が自動生成）
├── node_modules/       ← bun install が自動生成
├── index.html          ← フロントエンドのHTML
├── server.ts           ← ホットリロード対応の開発用Webサーバー
├── tsconfig.json       ← TypeScript コンパイラ設定
└── package.json        ← Bun プロジェクト設定
```

プロジェクト作成後は自動的に `myapp/` ディレクトリへカレントディレクトリが移動します。そのまま `tsbuild` を実行すれば開発を始められます。

---

## 🔄 自動バージョン更新

`tssetup` はコマンド実行時にGitHubから最新バージョンを自動確認します。新しいバージョンがある場合、自動でインストールスクリプトを取得して `$PROFILE` を更新します。手動で更新したい場合はインストールコマンドを再実行してください。

```powershell
irm https://raw.githubusercontent.com/Lapius7/tssetup/main/install.ps1 | iex
```

---

## 🗑️ アンインストール方法

`tssetup -Uninstall` を実行すると確認プロンプトが表示され、`y` を入力すると `$PROFILE` から `tssetup` 関数が削除されます。

```powershell
tssetup -Uninstall
```

```
⚠ tssetup をアンインストールします。本当によろしいですか？ (y/N): y
✅ tssetup をアンインストールしました。
```

アンインストールは現在のPowerShellセッション内でも即時反映されます。

---

## ✉️ 問い合わせ先

質問やフィードバック、バグ報告等は以下までご連絡ください。
*   **X (旧Twitter):** [@Lapius7](https://x.com/Lapius7)
*   **GitHub Issues:** [Lapius7/tssetup/issues](https://github.com/Lapius7/tssetup/issues)

---

## ⚠️ 免責事項

本ソフトウェア（スクリプト）の使用によって生じた、直接的・間接的な損害（データ消失、業務中断、PCの不具合等）について、作者は一切の責任を負いません。自己責任のもとでご使用ください。

---

## 📄 ライセンス & コピーライト

本プロジェクトは [MIT License](https://opensource.org/licenses/MIT) のもとで公開されています。

Copyright (c) 2026 Lapius7
