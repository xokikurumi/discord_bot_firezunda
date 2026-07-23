# ダイスロール詳細

## 1. 目的

Discord 上でダイス式を評価し、手動コマンドと通常メッセージの自動判定の両方で結果を返す。

## 2. クラス構成

| クラス | 役割 |
|---|---|
| DiceRollCog | `roll`/`dice` コマンドと自動ロール listener を提供する |
| DiceRollService | ダイス式判定と `d20` による評価を行う |

## 3. コマンド

| コマンド | 入力 | 処理 |
|---|---|---|
| `roll <expression>` | ダイス式文字列 | `d20.roll` の結果文字列を送信する |
| `dice <expression>` | `roll` の alias | 同上 |

式が空、または `d20` 評価で例外が発生した場合は `dice roll failed: {error}` を送信する。

## 4. 自動ロール

通常メッセージ受信時、次の条件をすべて満たす場合に自動ロールする。

| 条件 | 内容 |
|---|---|
| Bot 投稿でない | `message.author.bot` が false |
| guild 内投稿 | DM は対象外 |
| Service が enabled | `enabled=True` |
| content が空でない | strip 後に文字がある |
| command 風でない | `!`、`/`、`\` で始まらない |
| 正規表現一致 | 1 から 120 文字、少なくとも `数字 d 数字` を含む |

許可文字は数字、`dDkKhHlL`、四則演算、剰余、丸括弧、ピリオド、カンマ、空白である。

## 5. 評価

`roll(expression)` は入力を strip する。
空なら `ValueError("dice expression is empty.")` を送出する。
空でなければ `d20.roll(expression)` を実行し、戻り値を `str()` で文字列化して返す。
