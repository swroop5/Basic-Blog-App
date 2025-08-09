from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import json

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "posts.json"

def load_posts():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_posts(posts):
    DATA_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")

@app.route("/")
def index():
    return render_template("index.html", posts=load_posts())


def find_post_index(posts, post_id):
    """Return the index of the post with id=post_id, or None if not found."""
    for i, p in enumerate(posts):
        if p.get("id") == post_id:
            return i
    return None

@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    posts = load_posts()
    idx = find_post_index(posts, post_id)
    if idx is None:
        return "Post not found", 404

    if request.method == "POST":
        author  = (request.form.get("author")  or "").strip()
        title   = (request.form.get("title")   or "").strip()
        content = (request.form.get("content") or "").strip()

        if not author or not title or not content:
            # Re-render the form with an error and current inputs
            return render_template("update.html",
                                   post={"id": post_id, "author": author, "title": title, "content": content},
                                   error="All fields are required.")

        # Update the stored post
        posts[idx]["author"]  = author
        posts[idx]["title"]   = title
        posts[idx]["content"] = content
        save_posts(posts)
        return redirect(url_for("index"))

    # GET → show form pre-filled with current values
    return render_template("update.html", post=posts[idx])

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        posts = load_posts()
        new_id = (max((p["id"] for p in posts), default=0) + 1)
        post = {
            "id": new_id,
            "author": (request.form.get("author") or "").strip(),
            "title":  (request.form.get("title") or "").strip(),
            "content":(request.form.get("content") or "").strip(),
        }
        if not post["author"] or not post["title"] or not post["content"]:
            return render_template("add.html", error="All fields are required.", form=post)
        posts.append(post)
        save_posts(posts)
        return redirect(url_for("index"))
    return render_template("add.html")

# NEW: delete route
@app.route("/delete/<int:post_id>")
def delete(post_id: int):
    posts = load_posts()
    new_posts = [p for p in posts if p["id"] != post_id]
    # Only write back if something was actually removed
    if len(new_posts) != len(posts):
        save_posts(new_posts)
    # Either way, go back home
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Run: python app.py
    app.run(debug=True, port=5001)
