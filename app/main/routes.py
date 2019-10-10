from app import db
from datetime import datetime
from flask import (
    render_template, 
    flash, 
    redirect, 
    url_for,
    request
)
from app.main.forms import (
    EditProfileForm,
    PostForm,
)

from app.main.models import User, Post
from flask_login import (
    current_user, 
    login_user, 
    logout_user,
    login_required
)
from werkzeug.urls import url_parse
from app.main import bp
from flask import current_app

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
@login_required
def index():

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], True
    )

    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template(
        'index.html', 
        title='Hello!', 
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

@bp.route('/posts')
@login_required
def posts():

    posts = Post.query.all()

    return render_template(
        'posts.html', 
        title='Posts', 
        posts=posts
    )

@bp.route('/users/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(id = user_id).first_or_404()
    page = request.args.get('page', 1, type=int)

    posts = user.posts.order_by(
        Post.timestamp.desc()
    ).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )

    next_url = url_for('main.user', user_id=user.id, page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('main.user', user_id=user.id, page=posts.prev_num) \
        if posts.has_prev else None

    return render_template(
        'user.html', 
        user=user, 
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

@bp.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    if current_user.id != user_id:
        return redirect(url_for('main.user', user_id=current_user.id))
    
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Profile changes have been saved!')
        return redirect(url_for('edit_profile', user_id=current_user.id))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email 
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<int:user_id>')
@login_required
def follow(user_id):

    user = User.query.get(user_id)
    if user is None:
        flash('User {} does not exist!'.format(user_id))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You cant follow yourself! Thats silly!')
        return redirect(url_for('main.user', user_id=user_id))

    current_user.follow(user)
    db.session.commit()

    flash('You have followed {}!'.format(user.first_name))
    return redirect(url_for('main.user', user_id=user.id))

@bp.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):

    user = User.query.get(user_id)
    if user is None:
        flash('User {} does not exist!'.format(user_id))
        return redirect(url_for('main.index'))

    if user == current_user:
        flash('You cant unfollow yourself! Thats silly!')
        return redirect(url_for('main.user', user_id=user_id))

    current_user.unfollow(user)
    db.session.commit()

    flash('You are no longer following {}!'.format(user.first_name))
    return redirect(url_for('main.user', user_id=user.id))

@bp.route('/posts/create', methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():

        post = Post(
            title = form.title.data,
            body = form.body.data,
            author = current_user
        )

        db.session.add(post)
        db.session.commit()

        flash('Your post has been published!')
        return redirect(url_for('main.user', user_id=current_user.id))
    
    return render_template("create.html", title="Create Post", form=form)


@bp.route('/authors')
@login_required
def authors():

    page = request.args.get('page', 1, type=int)

    users = User.query.filter(
        User.id != current_user.id
    ).order_by(User.id.desc()).paginate(
        page, current_app.config['USERS_PER_PAGE'], False
    )

    next_url = url_for('main.authors', page=users.next_num) \
        if users.has_next else None

    prev_url = url_for('main.authors', page=users.prev_num) \
        if users.has_prev else None

    return render_template(
        'authors.html',
        title='Authors', 
        users=users.items,
        next_url=next_url,
        prev_url=prev_url
    )