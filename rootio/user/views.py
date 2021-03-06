# -*- coding: utf-8 -*-

import os
import uuid

from flask import url_for, redirect, current_app, request, flash, Blueprint, render_template, send_from_directory, abort
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from wtforms.validators import AnyOf
from wtforms import RadioField
from .models import User, UserDetail, NetworkInvitation
from rootio.decorators import admin_required
from rootio.user.forms import ProfileForm, ProfileCreateForm, NetworkInvitationForm
from rootio.radio.models import Network
from ..extensions import db
from .constants import USER_ROLE
from rootio.user import ADMIN
from ..utils import send_activation_email, send_invitation_email
from flask.ext.babel import gettext as _
from sqlalchemy import and_
from ..utils import send_activation_email


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    if not current_user.is_authenticated():
        abort(403)
    return render_template('user/index.html', user=current_user)

@user.route('/resend_activation', methods=['GET'])
def resend_activation():
    email = request.args.get('email')
    user = User.query.filter(and_(User.email == email)).first()
    send_activation_email(db, user)
    flash(_('A new activation link was sent via email'), 'info')
    return redirect(url_for('user.user_dashboard'))

@user.route('/<int:user_id>/profile')
def profile1(user_id):
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


@user.route('/<int:user_id>/avatar/<path:filename>')
@login_required
def avatar(user_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'user_%s' % user_id)
    return send_from_directory(dir_path, filename, as_attachment=True)


@user.route('/manager/')
@login_required
@admin_required
def user_dashboard():
    #Only the users in my networks
    if current_user.role_code == ADMIN:
        users = User.query.all()
    else:
        users = User.query.join(Network.networkusers).filter(Network.networkusers.contains(current_user)).all()
    return render_template('user/manager.html', user=current_user, users=users, active="Users")


@user.route('/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = ProfileCreateForm()
    if form.validate_on_submit():
        _user = User()
        _user.user_detail = UserDetail()
        form.populate_obj(_user)
        form.populate_obj(_user.user_detail)
        db.session.add(_user)
        db.session.commit()

        send_activation_email(db, _user)
        flash(_('User Created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('user/user.html', active="profile", form=form)


@user.route('/invite/', methods=['GET', 'POST'])
@login_required
@admin_required
def invite():

    invitation_key = "-".join([str(uuid.uuid1()), str(uuid.uuid4())])
    form = NetworkInvitationForm()
    form.role_code.choices = form.get_role_codes(current_user.role_code)
    new_invitations = False

    if form.validate_on_submit():
        try:
            for network in form.networks.data:
                if len(list(filter(lambda x: (x.email == form.email.data), network.networkusers))) < 1:
                    new_invitations = True
                    pending_invitation = NetworkInvitation\
                        .query.filter(NetworkInvitation.email == form.email.data and NetworkInvitation.deleted == False
                                      and NetworkInvitation.network_id == network.id).first()
                    if pending_invitation is None:
                        invitation = NetworkInvitation()
                        invitation.email = form.email.data
                        invitation.network_id = network.id
                        invitation.invited_by_user_id = current_user.id
                        invitation.role_code = form.role_code.data
                        invitation.invitation_key = invitation_key
                        db.session.add(invitation)
                        db.session.commit()

            if new_invitations:
                send_invitation_email(current_user, form.email.data)
                flash(_('User Invited.'), 'success')
            else:
                flash(_('The user already belongs to selected networks'))
        except Exception as e:
            print e

    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('user/invite.html', active="invite", form=form)


@user.route('/resend_invitation', methods=['GET'])
@login_required
@admin_required
def resend_invitation():
    try:
        email = request.args.get('email')
        send_invitation_email(current_user, email)
        flash(_('An Invitation email has been sent to %s' % email), 'info')
    except:
        flash(_('An error was encountered trying to re-send the invitation'), 'error')
    return redirect(url_for('user.invitations'))


@user.route('/invitations/', methods=['GET', 'POST'])
@login_required
@admin_required
def invitations():

    invites = NetworkInvitation.query.join(Network).filter(Network.networkusers.contains(current_user)).filter(
                                                                    NetworkInvitation.deleted == False).all()
    return render_template('user/invitations.html', active="Invitations", invitations=invites)


@user.route('/profile', methods=['GET', 'POST'], defaults={'user_id': None})
@user.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if user_id:
        edit = True
        user = User.query.get(user_id)
    else:
        edit = False
        user = User.query.filter_by(name=current_user.name).first_or_404()
    if not user.user_detail:
        user.user_detail = UserDetail()
    form = ProfileForm(obj=user.user_detail,
                       email=user.email,
                       name=user.name,
                       networks=user.networks,
                       role_code=user.role_code,
                       status_code=user.status_code,
                       next=request.args.get('next'))
    form.user_id = user.id
    form.role_code.choices = form.get_role_codes(current_user.role_code)
    if form.validate_on_submit():

        form.populate_obj(user)
        form.populate_obj(user.user_detail)
        form.populate_obj(user.networks)
        

        db.session.add(user)
        db.session.commit()

        flash('User profile successfully edited', 'success')

    return render_template('user/profile.html', user=user,
                           active="Users", form=form, in_settings=False, edit=edit)
