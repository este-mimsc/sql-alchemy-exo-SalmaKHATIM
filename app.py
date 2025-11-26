from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask( __name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    import models
    User = models.User
    Post = models.Post

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    # ------------------------------------- USERS -----------------------------------------
    @app.route("/users", methods=["GET", "POST"])
    def users():
        if request.method == "GET":
            all_users = User.query.all()
            users_list = [{"id": u.id, "username": u.username} for u in all_users]
            return jsonify(users_list), 200

        if request.method == "POST":
            data = request.get_json()
            if not data or "username" not in data:
                return jsonify({"error": "username is required"}), 400

            if User.query.filter_by(username=data["username"]).first():
                return jsonify({"error": "username already exists"}), 409

            new_user = User(username=data["username"])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"id": new_user.id, "username": new_user.username}), 201

    # ---------------------------------------- POSTS -----------------------------------
    @app.route("/posts", methods=["GET", "POST"])
    def posts():
        if request.method == "GET":
            all_posts = Post.query.all()
            posts_list = [
                {
                    "id": p.id,
                    "title": p.title,
                    "content": p.content,
                    "user_id": p.user_id,
                    "username": p.author.username if p.author else None,
                }
                for p in all_posts
            ]
            return jsonify(posts_list), 200

        if request.method == "POST":
            data = request.get_json()
            required_fields = ["title", "content", "user_id"]
            if not data or not all(field in data for field in required_fields):
                return jsonify({"error": "title, content, and user_id are required"}), 400

            user = User.query.get(data["user_id"])
            if not user:
                return jsonify({"error": "user_id does not exist"}), 404

            # CORRECTION ICI : utiliser user_id au lieu de author=user
            new_post = Post(
                title=data["title"], 
                content=data["content"], 
                user_id=data["user_id"]
            )
            db.session.add(new_post)
            db.session.commit()
            
            return jsonify({
                "id": new_post.id,
                "title": new_post.title,
                "content": new_post.content,
                "user_id": new_post.user_id,
                "username": new_post.author.username
            }), 201

    return app


app = create_app()

if __name__ == "_main_":
    app.run(debug=True)