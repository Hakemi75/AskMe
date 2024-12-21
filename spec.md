# メッセージボックスアプリケーション仕様書

## 概要
- Flaskフレームワークを使用したWebアプリケーション
- ORMとしてPeeweeを使用
- データベースとしてSQLiteを使用

## 機能一覧

### ユーザー認証機能
- 新規ユーザー登録
- ログイン
- ログアウト

### 質問投稿機能
- 質問の投稿(ログイン時のみ)
- 投稿一覧の表示

### 回答投稿機能
- 回答の投稿(ログイン時のみ)
- 回答一覧の表示(質問ごと)

### 質問/回答削除機能
- 質問の削除(ログイン時かつ自分の投稿のみ)
- 回答の削除(ログイン時かつ自分の投稿のみ)

### 評価機能
- 質問/回答に対する「グッド」ボタン
- 「グッド」の数の表示

### ランキング機能
- 上位10位のユーザーアカウントを表示
- ランキングは「グッド」の数と回答数で評価

### アカウント機能
- アカウント編集ボタン
- 自己紹介ページ
- 投稿履歴ページ
- 課金ページ

### 他ユーザー参照機能
- 他ユーザーアカウントの検索
- 他ユー��ーの自己紹介ページの閲覧

## データベース構造

### User
- id (PrimaryKey)
- name
- email
- password
- bio (自己紹介文)
- total_likes (獲得した「グッド」の総数)
- total_answers (投稿した回答の総数)

### Question
- id (PrimaryKey)
- user (User外部キー)
- content (質問内容)
- created_at
- likes (獲得した「グッド」の数)

### Answer
- id (PrimaryKey)
- user (User外部キー)
- question (Question外部キー)
- content (回答内容)
- created_at
- likes (獲得した「グッド」の数)

### Like
- id (PrimaryKey)
- user (User外部キー)
- question (Question外部キー) / answer (Answer外部キー)

## ルーティング
- / : ホーム(質問一覧)
- /register : 新規ユーザー登録
- /login : ログイン
- /logout : ログアウト
- /question/create : 質問投稿
- /question/<question_id> : 質問詳細(回答一覧)
- /answer/create/<question_id> : 回答投稿
- /question/<question_id>/delete : 質問削除
- /answer/<answer_id>/delete : 回答削除
- /like/question/<question_id> : 質問への「グッド」
- /like/answer/<answer_id> : 回答への「グッド」
- /ranking : ユーザーランキング
- /account/edit : アカウント編集
- /account/bio : 自己紹介ページ
- /account/posts : 投稿履歴
- /account/billing : 課金ページ
- /user/<user_id> : 他ユーザーの自己紹介ページ 
