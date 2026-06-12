# tssetup

PowerShellから1コマンドで、Bun + TypeScript の高速なフロントエンド開発環境（ホットリロードサーバー内蔵）を初期構築するツールです。

## 🚀 特徴

*   **瞬時にプロジェクト開始:** フォルダ作成、`bun init`、`tsconfig.json` の設定、ホットリロードサーバースクリプトの作成を自動で一括実行します。
*   **多彩な初期テンプレート:**
    *   `default`: Destyle.cssを内包したシンプルな構成（ダークモード対応）。
    *   `tailwind`: CDN版Tailwind CSSが即座に使えるレイアウト構成。
    *   `router`: ライブラリを使わずにHTML5 History APIを利用した、自作の超軽量SPAルーティング構成。
    *   `empty`: 最少構成（空のTypeScriptファイルとシンプルなHTML）。
*   **エディタ連携:** `--Code` オプションを付けるだけで、作成したプロジェクトフォルダをVS Codeで即座に開きます。

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

### パラメータ（引数）詳細

| パラメータ名 | エイリアス | 型 | 必須 | デフォルト値 | 説明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ProjectName`** | (位置引数 `0`) | `string` | **はい** | - | 作成するプロジェクトのフォルダ名。相対パス・絶対パスが指定可能です。 |
| **`-Mode`** | `-m` | `string` | いいえ | `default` | テンプレートの初期構造。`default`, `tailwind`, `router`, `empty` から選択。 |
| **`-Title`** | `-t` | `string` | いいえ | `"Bun + TS App"` | 生成される `index.html` の `<title>` タグに埋め込まれるテキスト。 |
| **`-Code`** | `-c` | `switch` | いいえ | `$false` | 指定すると、セットアップ完了直後に自動で VS Code でプロジェクトを開きます。 |
| **`-Help`** | `-h` | `switch` | いいえ | `$false` | コマンドのヘルプメッセージ（使い方とオプション）を表示して終了します。 |

---

### コマンド実行例（ユースケース別）

#### 1. 最もシンプルな基本構成で作成する
```powershell
tssetup my-app
```
`my-app` フォルダがカレントディレクトリ配下に作成され、自動的に `bun init` や `tsconfig.json` が配置されます。

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


