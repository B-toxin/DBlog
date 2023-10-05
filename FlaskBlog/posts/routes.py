from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from FlaskBlog import db
from FlaskBlog.models import Post, Comment
from FlaskBlog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@posts.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
@login_required
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()

    if form.validate_on_submit():
        content = form.content.data
        new_comment = Comment(content=content, author=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))

    return render_template('comment.html', post=post, form=form)


@posts.route('/submit_comment/<int:post_id>', methods=['POST'])
def submit_comment(post_id):
    content = request.form.get('content')

    # Check if the user is logged in
    if not current_user.is_authenticated:
        # Handle the case where the user is not logged in (redirect to login page or show an error message)
        flash('You need to be logged in to submit a comment.', 'danger')
        return redirect(url_for('login'))  # Redirect to the login page and display an error message

    if content:
        post = Post.query.get_or_404(post_id)
        new_comment = Comment(content=content, author=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')

    return redirect(url_for('posts.post', post_id=post_id))


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    # Delete associated comments
    comments = Comment.query.filter_by(post_id=post.id).all()
    for comment in comments:
        db.session.delete(comment)

    # Delete the post itself
    db.session.delete(post)
    db.session.commit()

    flash('Your post and its comments have been deleted!', 'success')
    return redirect(url_for('main.home'))
