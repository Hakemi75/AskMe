from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import database, User, Question, Answer, Comment, Like
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# LoginManagerの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id == int(user_id))


# データベース接続の設定
@app.before_request
def before_request():
    database.connect()


@app.after_request
def after_request(response):
    database.close()
    return response


# ルートページ（質問一覧）
@app.route("/")
def index():
    questions = Question.select().order_by(Question.created_at.desc())
    return render_template("index.html", questions=questions)


# 新規ユーザー登録
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([name, email, password]):
            flash("全ての項目を入力してください")
            return redirect(url_for("register"))

        if User.select().where(User.email == email).exists():
            flash("このメールアドレスは既に登録されています")
            return redirect(url_for("register"))

        user = User.create(
            name=name,
            email=email,
            password=generate_password_hash(password),
            bio="",
            total_likes=0,
            total_answers=0,
        )
        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html")


# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([email, password]):
            flash("メールアドレスとパスワードを入力してください")
            return redirect(url_for("login"))

        user = User.get_or_none(User.email == email)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))

        flash("メールアドレスまたはパスワードが間違っています")

    return render_template("login.html")


# ログアウト
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# 質問投稿
@app.route("/question/create", methods=["GET", "POST"])
@login_required
def question_create():
    if request.method == "POST":
        content = request.form.get("content")
        if content:
            Question.create(user=current_user.id, content=content, likes=0)
            flash("質問を投稿しました")
            return redirect(url_for("index"))
        flash("質問内容を入力してください")
    return render_template("question_create.html")


# 質問詳細
@app.route("/question/<int:question_id>")
def question_detail(question_id):
    question = Question.get_or_none(Question.id == question_id)
    if question:
        # 回答をいいね数の多い順に並び替え
        answers = (
            Answer.select()
            .where(Answer.question == question)
            .order_by(Answer.likes.desc(), Answer.created_at.desc())
        )
        return render_template("question_detail.html", question=question, answers=answers, Like=Like)
    return redirect(url_for("index"))


# 質問削除
@app.route("/question/<int:question_id>/delete")
@login_required
def question_delete(question_id):
    question = Question.get_or_none(Question.id == question_id)
    if question and question.user.id == current_user.id:
        # 関連する回答とイイネを削除
        for answer in question.answers:
            Like.delete().where(Like.answer == answer).execute()
            Comment.delete().where(Comment.answer == answer).execute()
        Like.delete().where(Like.question == question).execute()
        Answer.delete().where(Answer.question == question).execute()
        question.delete_instance()
        flash("質問を削除しました")
    return redirect(url_for("index"))


# 回答投稿
@app.route("/answer/create/<int:question_id>", methods=["POST"])
@login_required
def answer_create(question_id):
    question = Question.get_or_none(Question.id == question_id)
    if question:
        content = request.form.get("content")
        if content:
            Answer.create(user=current_user.id, question=question, content=content, likes=0)
            current_user.total_answers += 1
            current_user.save()
            flash("回答を投稿しました")
        else:
            flash("回答内容を入力してください")
    return redirect(url_for("question_detail", question_id=question_id))


# 回答削除
@app.route("/answer/<int:answer_id>/delete")
@login_required
def answer_delete(answer_id):
    answer = Answer.get_or_none(Answer.id == answer_id)
    if answer and answer.user.id == current_user.id:
        question_id = answer.question.id
        # コメントとイイネを削除
        Comment.delete().where(Comment.answer == answer).execute()
        Like.delete().where(Like.answer == answer).execute()
        answer.user.total_answers -= 1
        answer.user.save()
        answer.delete_instance()
        flash("回答を削除しました")
        return redirect(url_for("question_detail", question_id=question_id))
    return redirect(url_for("index"))


# 質問へのイイネ
@app.route("/like/question/<int:question_id>", methods=["POST"])
@login_required
def like_question(question_id):
    question = Question.get_or_none(Question.id == question_id)
    if question:
        like = Like.get_or_none(Like.user == current_user.id, Like.question == question)
        if like:
            like.delete_instance()
            question.likes -= 1
            question.user.total_likes -= 1
            flash("イイネを取り消しました")
        else:
            Like.create(user=current_user.id, question=question)
            question.likes += 1
            question.user.total_likes += 1
            flash("イイネしました")
        question.save()
        question.user.save()
    return redirect(url_for("question_detail", question_id=question_id))


# 回答へのイイネ
@app.route("/like/answer/<int:answer_id>", methods=["POST"])
@login_required
def like_answer(answer_id):
    answer = Answer.get_or_none(Answer.id == answer_id)
    if answer:
        like = Like.get_or_none(Like.user == current_user.id, Like.answer == answer)
        if like:
            like.delete_instance()
            answer.likes -= 1
            answer.user.total_likes -= 1
            flash("イイネを取り消しました")
        else:
            Like.create(user=current_user.id, answer=answer)
            answer.likes += 1
            answer.user.total_likes += 1
            flash("イイネしました")
        answer.save()
        answer.user.save()
    return redirect(url_for("question_detail", question_id=answer.question.id))


# ユーザープロフィール
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = User.get_or_none(User.id == user_id)
    if user:
        return render_template("user_profile.html", user=user)
    return redirect(url_for("index"))


# アカウント編集
@app.route("/account/edit", methods=["GET", "POST"])
@login_required
def account_edit():
    if request.method == "POST":
        name = request.form.get("name")
        bio = request.form.get("bio")
        youtube_url = request.form.get("youtube_url")
        twitter_url = request.form.get("twitter_url")
        github_url = request.form.get("github_url")
        website_url = request.form.get("website_url")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")

        if not name:
            flash("ユーザー名を入力してください")
            return redirect(url_for("account_edit"))

        current_user.name = name
        current_user.bio = bio or ""
        current_user.youtube_url = youtube_url or None
        current_user.twitter_url = twitter_url or None
        current_user.github_url = github_url or None
        current_user.website_url = website_url or None

        if current_password and new_password:
            if check_password_hash(current_user.password, current_password):
                current_user.password = generate_password_hash(new_password)
            else:
                flash("現在のパスワードが間違っています")
                return redirect(url_for("account_edit"))

        current_user.save()
        flash("プロフィールを更新しました")
        return redirect(url_for("user_profile", user_id=current_user.id))

    return render_template("account_edit.html")


# ランキング
@app.route("/ranking")
def ranking():
    users = User.select().order_by(User.total_likes.desc(), User.total_answers.desc()).limit(10)
    return render_template("ranking.html", users=users)


# 回答へのコメント投稿
@app.route("/comment/create/<int:answer_id>", methods=["POST"])
@login_required
def comment_create(answer_id):
    answer = Answer.get_or_none(Answer.id == answer_id)
    if answer:
        content = request.form.get("content")
        if content:
            Comment.create(user=current_user.id, answer=answer, content=content)
            flash("コメントを投稿しました")
        else:
            flash("コメント���容を入力してください")
        return redirect(url_for("question_detail", question_id=answer.question.id))
    return redirect(url_for("index"))


# コメント削除
@app.route("/comment/<int:comment_id>/delete")
@login_required
def comment_delete(comment_id):
    comment = Comment.get_or_none(Comment.id == comment_id)
    if comment and comment.user.id == current_user.id:
        question_id = comment.answer.question.id
        comment.delete_instance()
        flash("コメントを削除しました")
        return redirect(url_for("question_detail", question_id=question_id))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
