# -*- coding: utf-8 -*-

import os
import urllib
from datetime import datetime

from flask import Blueprint, render_template, request, flash, jsonify
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user

from rootio.config import DefaultConfig
from telephony.cereproc.cereproc_rest_agent import CereprocRestAgent
from ..content.forms import CommunityMenuForm
from ..content.models import CommunityMenu
from models import VoicePrompt
from ..extensions import db, csrf
from ..radio.forms import StationForm
from .forms import StationTelephonyForm, StationSipTelephonyForm, StationAudioLevelsForm, StationSynchronizationForm, StationTtsForm, VoicePromptForm
from ..radio.models import Station, Network
from ..user.models import User
from ..utils import upload_to_s3, make_dir, save_uploaded_file, jquery_dt_paginator

configuration = Blueprint('configuration', __name__, url_prefix='/configuration')


@configuration.route('/', methods=['GET'])
def index():
    # get all the user's networks and their stations
    networks = Network.query.outerjoin(Station).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/index.html', networks=networks, userid=current_user.id, now=datetime.now)


@configuration.route('/tts/', methods=['GET'])
def tts():
    stations = Station.query.all()
    # demo, override station statuses
    for s in stations:
        s.status = "on"

    # end demo
    return render_template('configuration/tts.html', stations=stations)


@configuration.route('/telephony/', methods=['GET', 'POST'])
def telephony():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/stations_telephony.html', stations=stations)


@configuration.route('/telephony/<int:station_id>', methods=['GET', 'POST'])
def telephony_station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationTelephonyForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Station updated.'), 'success')

    return render_template('configuration/station_telephony.html', station=station, form=form)


@configuration.route('/telephony/add/', methods=['GET', 'POST'])
@login_required
def telephony_add():
    form = StationTelephonyForm(request.form)
    station = None

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('phone_inline', None)  # and also inline forms
        cleaned_data.pop('location_inline', None)
        station = Station(**cleaned_data)  # create new object from data

        db.session.add(station)
        db.session.commit()
        flash(_('Station added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('configuration/station_telephony.html', station=station, form=form)


@configuration.route('/sip_configuration/<int:station_id>', methods=['GET', 'POST'])
@login_required
def sip_configuration(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationSipTelephonyForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('SIP details updated.'), 'success')

    return render_template('configuration/sip_configuration.html', station=station, form=form)


@configuration.route('/sip_telephony', methods=['GET', 'POST'])
def sip_telephony():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/sip_telephony.html', stations=stations)


@configuration.route('/station_audio_level/<int:station_id>', methods=['GET', 'POST'])
def station_audio_level(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationAudioLevelsForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Audio levels updated.'), 'success')

    return render_template('configuration/station_audio_level.html', station=station, form=form)


@configuration.route('/station_audio_levels', methods=['GET'])
def station_audio_levels():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/station_audio_levels.html', stations=stations, active='stations')


@configuration.route('/ivr_menus', methods=['GET', 'POST'])
def ivr_menus():
    community_menus = CommunityMenu.query.join(Station).join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/ivr_menus.html', community_menus=community_menus)


@configuration.route('/ivr_menus/records', methods=['GET'])
# @returns_json
def ivr_menu_records(**kwargs):
    from ..user.models import User
    from ..radio.models import Station, Network
    cols = [CommunityMenu.station, CommunityMenu.use_tts, CommunityMenu.welcome_message, CommunityMenu.welcome_message_txt, CommunityMenu.days_prompt, CommunityMenu.days_prompt_txt, CommunityMenu.record_prompt, CommunityMenu.record_prompt_txt,
            CommunityMenu.finalization_prompt, CommunityMenu.finalization_prompt_txt, CommunityMenu.goodbye_message, CommunityMenu.goodbye_message_txt]
    ivr_menus = CommunityMenu.query.with_entities(*cols).join(Station).join(Network).join(User, Network.networkusers).filter(
        User.id == current_user.id)

    records = jquery_dt_paginator.get_records(ivr_menus, [CommunityMenu.welcome_message_txt, CommunityMenu.message_type_prompt_txt, CommunityMenu.days_prompt_txt, CommunityMenu.record_prompt_txt, CommunityMenu.finalization_prompt_txt, CommunityMenu.goodbye_message_txt], request)
    return jsonify(records)


@configuration.route('/ivr_menus/<int:ivr_menu_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def ivr_menu_delete(ivr_menu_id):
    ivr_menu = CommunityMenu.query.filter_by(id=ivr_menu_id).first_or_404()

    ivr_menu.deleted = True

    try:
        db.session.add(ivr_menu)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@configuration.route('/ivr_menu', methods=['GET', 'POST'])
@login_required
def ivr_menu():
    form = CommunityMenuForm(request.form)
    station = form.station
    community_menu = None
    if request.method == 'POST':
        pass  # validate files here
    if form.validate_on_submit():
        station = request.form['station']
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)
        for key in request.files.keys():
            prompt_file = request.files[key]
            file_path = os.path.join("community-menu", station)
            uri = save_uploaded_file(prompt_file, file_path)
            cleaned_data[key] = uri

        community_menu = CommunityMenu(**cleaned_data)  # create new object from data

        if cleaned_data['use_tts'] and cleaned_data['prefetch_tts']:
            cereproc_agent = CereprocRestAgent(DefaultConfig.CEREPROC_SERVER, DefaultConfig.CEREPROC_USERNAME, DefaultConfig.CEREPROC_PASSWORD)
            prompts_fetched = True
            for key in cleaned_data.keys():
                if prompts_fetched and str(key).endswith("txt"):
                    try:
                        file_url = cereproc_agent.get_cprc_tts(cleaned_data[key].encode('utf-8'), community_menu.station.tts_voice.name, community_menu.station.tts_samplerate.value, community_menu.station.tts_audioformat.name)[0]
                        dest_file = os.path.join(file_path, file_url.split('/').pop())
                        urllib.urlretrieve(file_url, os.path.join(DefaultConfig.CONTENT_DIR, dest_file))
                        setattr(community_menu, key[:-4], dest_file)
                        prompts_fetched = True
                    except Exception as e:
                        print e
                        prompts_fetched = False

            if prompts_fetched:
                setattr(community_menu, 'use_tts', False)

        db.session.add(community_menu)
        db.session.commit()

        flash(_('Configuration saved.'), 'success')

    elif request.method == "POST":
        flash(_(form.errors.items()), 'error')

    return render_template('configuration/ivr_menu.html', community_menu=community_menu, form=form, station=station)


@configuration.route('/tts_settings', methods=['GET', 'POST'])
@login_required
def tts_settings():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/tts_settings.html', stations=stations)


@configuration.route('/tts_setting/<int:station_id>', methods=['GET', 'POST'])
@login_required
def tts_setting(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationTtsForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('TTS settings updated.'), 'success')

    return render_template('configuration/tts_setting.html', station=station, form=form)


@configuration.route('/synchronization_settings', methods=['GET', 'POST'])
@login_required
def synchronization_settings():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/synchronization_settings.html', stations=stations)


@configuration.route('/synchronization_setting/<int:station_id>', methods=['GET', 'POST'])
@login_required
def synchronization_setting(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationSynchronizationForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Synchronization settings updated.'), 'success')

    return render_template('configuration/synchronization_setting.html', station=station, form=form)


@configuration.route('/voice_prompts', methods=['GET', 'POST'])
def voice_prompts():
    voice_prompts = VoicePrompt.query.join(Station).join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/voice_prompts.html', voice_prompts=voice_prompts)


@configuration.route('/voice_prompt', methods=['GET', 'POST'])
@login_required
def voice_prompt():
    form = VoicePromptForm(request.form)
    station = form.station
    voice_prompt = None
    if request.method == 'POST':
        pass  # validate files here
    if form.validate_on_submit():
        station = request.form['station']
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)
        for key in request.files.keys():
            prompt_file = request.files[key]
            file_path = os.path.join("voice-prompt", station)
            uri = save_uploaded_file(prompt_file, file_path)
            cleaned_data[key] = uri

        voice_prompt = VoicePrompt(**cleaned_data)  # create new object from data

        if cleaned_data['use_tts'] and cleaned_data['prefetch_tts']:
            cereproc_agent = CereprocRestAgent(DefaultConfig.CEREPROC_SERVER, DefaultConfig.CEREPROC_USERNAME, DefaultConfig.CEREPROC_PASSWORD)
            prompts_fetched = True
            for key in cleaned_data.keys():
                if prompts_fetched and str(key).endswith("txt"):
                    try:
                        file_url = cereproc_agent.get_cprc_tts(cleaned_data[key].encode('utf-8'), voice_prompt.station.tts_voice.name, voice_prompt.station.tts_samplerate.value, voice_prompt.station.tts_audioformat.name)[0]
                        dest_file = os.path.join(file_path, file_url.split('/').pop())
                        urllib.urlretrieve(file_url, os.path.join(DefaultConfig.CONTENT_DIR, dest_file))
                        setattr(voice_prompt, key[:-4], dest_file)
                        prompts_fetched = True
                    except Exception as e:
                        print e
                        prompts_fetched = False

            if prompts_fetched:
                setattr(voice_prompt, 'use_tts', False)

        db.session.add(voice_prompt)
        db.session.commit()

        flash(_('Configuration saved.'), 'success')

    elif request.method == "POST":
        flash(_(form.errors.items()), 'error')

    return render_template('configuration/voice_prompt.html', voice_prompt=voice_prompt, form=form, station=station)


@configuration.route('/voice_prompts/<int:voice_prompt_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def voice_prompt_delete(voice_prompt_id):
    voice_prompt = VoicePrompt.query.filter_by(id=voice_prompt_id).first_or_404()

    voice_prompt.deleted = True

    try:
        db.session.add(voice_prompt)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'
