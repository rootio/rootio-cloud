# -*- coding: utf-8 -*-

import uuid
from sqlalchemy import and_
from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort)
from flask.ext.mail import Message
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh

from .utils import RootIOMailMessage
from ..user import User, UserDetail
from ..extensions import db, mail, login_manager, oid
from ..user.constants import ACTIVE
from .forms import SignupForm, LoginForm, RecoverPasswordForm, ReauthForm, ChangePasswordForm, OpenIDForm, \
    CreateProfileForm

frontend = Blueprint('frontend', __name__)


@frontend.route('/login/openid', methods=['GET', 'POST'])
@oid.loginhandler
def login_openid():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = OpenIDForm()
    if form.validate_on_submit():
        openid = form.openid.data
        return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('frontend/login_openid.html', form=form, error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user and login_user(user):
        flash(_('Logged in'), 'success')
        return redirect(oid.get_next_url() or url_for('user.index'))
    return redirect(url_for('frontend.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname, email=resp.email,
                            openid=resp.identity_url))


@frontend.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = CreateProfileForm(name=request.args.get('name'),
                             email=request.args.get('email'),
                             openid=request.args.get('openid'))

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.activation_key = "-".join([str(uuid.uuid1()), str(uuid.uuid4())])
        db.session.add(user)
        db.session.commit()

        if login_user(user):
            return redirect(url_for('user.index'))

    return render_template('frontend/create_profile.html', form=form)


@frontend.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    page = int(request.args.get('page', 1))
    pagination = User.query.paginate(page=page, per_page=10)
    return render_template('index.html', pagination=pagination)


@frontend.route('/search')
def search():
    keywords = request.args.get('keywords', '').strip()
    pagination = None
    if keywords:
        page = int(request.args.get('page', 1))
        pagination = User.search(keywords).paginate(page, 1)
    else:
        flash(_('Please input keyword(s)'), 'error')
    return render_template('frontend/search.html', pagination=pagination, keywords=keywords)


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = LoginForm(login=request.args.get('login', None),
                     next=request.args.get('next', None))

    if form.validate_on_submit():
        user, authenticated, activated = User.authenticate(form.login.data,
                                                           form.password.data)

        if user and authenticated and activated:
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash(_("Logged in"), 'success')
            return redirect(form.next.data or url_for('user.index'))
        else:
            if user and authenticated:
                flash(_('This account is not yet activated. Please click the link sent to you to activate'), 'error')
                return render_template('frontend/resend_activation.html', form=form, email=user.email)
            else:
                flash(_('Invalid login details. Please try again'))

    return render_template('frontend/login.html', form=form)


@frontend.route('/resend_activation', methods=['GET'])
def resend_activation():
    email = request.args.get('email')
    user = User.query.filter(and_(User.email == email)).first()
    send_activation_email(user)
    flash(_('A new activation link was sent to you via email, please check your inbox!'), 'info')
    return render_template('frontend/login.html', form=LoginForm())


@frontend.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    form = ReauthForm(next=request.args.get('next'))

    if request.method == 'POST':
        user, authenticated = User.authenticate(current_user.name,
                                                form.password.data)
        if user and authenticated:
            confirm_login()
            flash(_('Reauthenticated.'), 'success')
            return redirect('/change_password')

        flash(_('Password is wrong.'), 'error')
    return render_template('frontend/reauth.html', form=form)


@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logged out'), 'success')
    return redirect(url_for('frontend.index'))


@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated():
        return redirect(url_for('user.index'))

    form = SignupForm(next=request.args.get('next'))

    if form.validate_on_submit():
        user = User()
        user.user_detail = UserDetail()
        form.populate_obj(user)

        send_activation_email(user)

        flash(_('Your account was created. Please click on the link sent to your email to validate it'), 'success')
    return render_template('frontend/signup.html', form=form)

def send_activation_email(user):
    user.activation_key = "-".join([str(uuid.uuid1()), str(uuid.uuid4())])
    db.session.add(user)
    db.session.commit()

    # send the email with the link
    message = RootIOMailMessage()
    message.set_subject("Your RootIO platform account")
    message.set_body("Welcome to the RootIO platform!\n")
    message.append_to_body("Your username is %s " % user.email)
    message.append_to_body(
        "Please click this link to activate your account: %s/activate/%s/%d" % (
            current_app.config['DOMAIN'], user.activation_key, user.id
        )
    )
    message.append_to_body("\n\nThanks,\nThe RootIO team")
    message.set_from(current_app.config['DEFAULT_MAIL_SENDER'])
    message.add_to_address(user.email)
    message.send_message()
    # if login_user(user):
    #    return redirect(form.next.data or url_for('user.index'))


@frontend.route('/terms')
def terms():
    return render_template('frontend/terms.html')


@frontend.route('/activate/<string:key>/<int:user_id>', methods=['GET'])
def activate(key, user_id):
    if key is None or user_id is None:
        flash(_('Invalid link'), 'error')
    user = User.query.filter(and_(User.activation_key == key, User.id == user_id, User.status_code == 0)).first()
    if user is None:
        flash(_('No user found. This account is probably already validated, try logging in'), 'error')
    else:
        user.status_code = ACTIVE
        db.session.commit()
        flash(_('This account has successfully been validated, please login'), 'success')
    return redirect(url_for('frontend.login'))


@frontend.route('/change_password', methods=['GET', 'POST'])
def change_password():
    user = None
    if current_user.is_authenticated():
        if not login_fresh():
            return login_manager.needs_refresh()
        user = current_user
    elif 'activation_key' in request.values and 'email' in request.values:
        activation_key = request.values['activation_key']
        email = request.values['email']
        user = User.query.filter_by(activation_key=activation_key) \
            .filter_by(email=email).first()

    if user is None:
        abort(403)

    form = ChangePasswordForm(activation_key=user.activation_key, email=user.email)

    if form.validate_on_submit():
        user.password = form.password.data
        user.activation_key = None
        db.session.add(user)
        db.session.commit()

        flash(_("Your password has been changed, please log in again"), "success")
        return redirect(url_for("frontend.login"))

    return render_template("frontend/change_password.html", form=form)


@frontend.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash(_('Please see your email for instructions on how to access your account'), 'success')

            user.activation_key = str(uuid.uuid4())
            db.session.add(user)
            db.session.commit()

            url = url_for('frontend.change_password', email=user.email, activation_key=user.activation_key,
                          _external=True)
            html = render_template('macros/_reset_password.html', project=current_app.config['PROJECT'],
                                   username=user.name, url=url)
            message = RootIOMailMessage()
            message.set_subject('[{}] Reset your password'.format(current_app.config['PROJECT']))
            message.set_body(html)
            message.set_from(current_app.config['DEFAULT_MAIL_SENDER'])
            message.add_to_address(user.email)
            message.send_message()

            return render_template('frontend/reset_password.html', form=form)
        else:
            flash(_('Sorry, no user found for that email address'), 'error')

    return render_template('frontend/reset_password.html', form=form)


@frontend.route('/help')
def help():
    return render_template('frontend/footers/help.html', active="help")


@frontend.route('/lang/', methods=['POST'])
def lang():
    session['language'] = request.form['language']
    new_language = current_app.config['ACCEPT_LANGUAGES'][request.form['language']]
    flash(_('Language changed to ') + new_language, 'success')
    return redirect(url_for('frontend.index'))
