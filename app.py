from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
import json

app = Flask(__name__)

# JSON file used for storing blog posts
DATA_FILE = Path(__file__).parent / "posts.json"


def load_posts():
    """
    Load posts from the JSON data file.

    Ensures that the data file exists; if not, it creates an empty list file.

    Returns:
        list[dict]: A list of post dictionaries loaded from the JSON file.
    """
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_posts(posts):
    """
    Save the list of posts to the JSON data file.

    Args:
        posts (list[dict]): The list of post dictionaries to be saved.
    """
    DATA_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")


@app.route("/")
def index():
    """
    Display the homepage with all blog posts.

    Returns:
        Response: Rendered HTML template showing the list of posts.
    """
    return render_template("index.html", posts=load_posts())


def find_post_index(posts, post_id):
    """
    Find the index of a post by its ID.

    Args:
        posts (list[dict]): The list of posts.
        post_id (int): The ID of the post to find.

    Returns:
        int | None: The index of the post in the list, or None if not found.
    """
    for i, p in enumerate(posts):
        if p.get("id") == post_id:
            return i
    return None


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """
    Update an existing post by ID.

    GET:
        Displays a form pre-filled with the current post values.
    POST:
        Validates input and updates the post if all fields are filled.

    Args:
        post_id (int): The ID of the post to update.

    Returns:
        Response: Rendered form on GET or failed POST,
                  redirect to index on success,
                  or 404 if post not found.
    """
    posts = load_posts()
    idx = find_post_index(posts, post_id)
    if idx is None:
        return "Post not found", 404

    if request.method == "POST":
        author = (request.form.get("author") or "").strip()
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()

        if not author or not title or not content:
            # Re-render the form with an error and current inputs
            return render_template("update.html",
                                   post={"id": post_id, "author": author, "title": title, "content": content},
                                   error="All fields are required.")

        # Update the stored post
        posts[idx]["author"] = author
        posts[idx]["title"] = title
        posts[idx]["content"] = content
        save_posts(posts)
        return redirect(url_for("index"))

    # GET → show form pre-filled with current values
    return render_template("update.html", post=posts[idx])


@app.route("/add", methods=["GET", "POST"])
def add():
    """
    Add a new post.

    GET:
        Renders an empty form to create a new post.
    POST:
        Validates input, assigns a new ID, and saves the post.

    Returns:
        Response: Rendered form on GET or failed POST,
                  redirect to index on success.
    """
    if request.method == "POST":
        posts = load_posts()
        new_id = (max((p["id"] for p in posts), default=0) + 1)
        post = {
            "id": new_id,
            "author": (request.form.get("author") or "").strip(),
            "title": (request.form.get("title") or "").strip(),
            "content": (request.form.get("content") or "").strip(),
        }
        if not post["author"] or not post["title"] or not post["content"]:
            return render_template("add.html", error="All fields are required.", form=post)
        posts.append(post)
        save_posts(posts)
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<int:post_id>")
def delete(post_id: int):
    """
    Delete a post by ID.

    Args:
        post_id (int): The ID of the post to delete.

    Returns:
        Response: Redirects to the index page whether or not a post was deleted.
    """
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
