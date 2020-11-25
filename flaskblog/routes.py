import flask
import smtplib
import ssl
import os
import secrets
import flaskblog.models as models   # 'modles.py' file
import flaskblog.forms as forms     # 'forms.py' file
from flaskblog import app, bcrypt, db  # , mail
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = flask.request.args.get('page', 1, type=int)
    posts = models.Post.query.order_by(
        models.Post.date_posted.desc()).paginate(per_page=4, page=page)
    return flask.render_template('home.html', posts=posts, title="FlaskBlog")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.LoginFrom()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)

            # args is a dict. we don't use args['next'] because if we didn't redirect to login
            #   page from account page - it won't be exists and will raise an error
            #   in the case if it's not exists - None will returned.
            next_page = flask.request.args.get('next')
            if next_page:
                return flask.redirect(next_page)
            else:
                flask.flash('Account Logged in!', 'success')
                return flask.redirect(flask.url_for('home'))
        else:
            flask.flash(
                'Login Unseccessful. Please check the data amd try again.', 'danger')
    return flask.render_template('login.html', title="Login", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = forms.RegistrationFrom()
    if form.validate_on_submit():
        form.password.data = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = models.User(username=form.username.data,
                           email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flask.flash(
            f'Account created!\n Hello {form.username.data}!', 'success')
        return flask.redirect(flask.url_for('home'))

    return flask.render_template('register.html', title="Register", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flask.flash(f'Account Logout successfully', 'success')
    return flask.redirect(flask.url_for('home'))


def save_pic(form_pic_data):
    rand_hex = secrets.token_hex(8)
    file_name, f_ext = os.path.splitext(form_pic_data.filename)
    pic_f_name = rand_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/pics', pic_f_name)
    form_pic_data.save(pic_path)
    return pic_f_name


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = forms.UpdateAccountFrom()
    if form.validate_on_submit():
        if form.picture.data:
            pic_file = save_pic(form.picture.data)
            current_user.image_file = pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flask.flash(f'Account Info has been updated successfully!', 'success')
        return flask.redirect(flask.url_for('account'))
    elif flask.request.method == 'GET':  # show in the HTML the username+email
        form.username.data = current_user.username
        form.email.data = current_user.email

    image = flask.url_for('static', filename=f'pics/{current_user.image_file}')
    return flask.render_template('account.html', title="Account", image_file=image, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def newPost():
    form = forms.PostForm()
    if form.validate_on_submit():
        post = models.Post(title=form.title.data,
                           content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flask.flash(f'Post created!', 'success')
        return flask.redirect(flask.url_for('home'))

    return flask.render_template('managePost.html', title="New Post", form=form)


@app.route("/post/<int:post_id>")
def showPost(post_id):
    post = models.Post.query.get_or_404(post_id)
    return flask.render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def updatePost(post_id):
    post = models.Post.query.get_or_404(post_id)
    if post.author != current_user:
        flask.abort(403)
    form = forms.PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flask.flash(f'Post Update!', 'success')
        return flask.redirect(flask.url_for('home'))
    elif flask.request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return flask.render_template('managePost.html', title="Update Post", post=post, form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def deletePost(post_id):
    post = models.Post.query.get_or_404(post_id)
    if post.author != current_user:
        flask.abort(403)
    db.session.delete(post)
    db.session.commit()
    flask.flash(f'Post has been deleted!', 'success')
    return flask.redirect(flask.url_for('home'))


@app.route("/posts/<string:username>", methods=['GET', 'POST'])
@login_required
def userPosts(username):
    page = flask.request.args.get('page', 1, type=int)
    user = models.User.query.filter_by(username=username).first_or_404()
    posts = models.Post.query.filter_by(author=user)\
        .order_by(models.Post.date_posted.desc())\
        .paginate(per_page=4, page=page)
    return flask.render_template('userPosts.html', posts=posts, user=user, title="My Blogs")


def sendResetEmail(user):
    return user.get_reset_token()

#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='shachar.markovich@gmail.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {flask.url_for('resetMyPassword', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)


@app.route("/reset-password", methods=['GET', 'POST'])
def resetRequest():
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))

    form = forms.RequestResetForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        token = sendResetEmail(user)
        flask.flash('An Email has been sent to your Email!', 'info')
        return flask.redirect(flask.url_for('resetMyPassword', token=token))

    return flask.render_template('resetRequest.html', form=form, title='Reset Request')


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def resetMyPassword(token):
    if current_user.is_authenticated:
        return flask.redirect(flask.url_for('home'))

    user = models.User.varify_reset_token(token)
    if not user:  # if token expired:
        flask.flash('Invaild token! Token had been expired', 'warning')
        return flask.redirect(flask.url_for('resetRequest'))

    form = forms.ResetPasswordForm()
    if form.validate_on_submit():  # when the user fill the reset password form
        user.password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        db.session.commit()
        flash('Your password has been updated! You are now able to log in!', 'success')
        return redirect(url_for('login'))

    return flask.render_template('resetToken.html', form=form, title='Reset Password')
