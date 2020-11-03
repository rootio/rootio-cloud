import pytz, datetime

from coaster.sqlalchemy import BaseMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from ..extensions import db
from ..utils import STRING_LEN
import datetime


t_tracknetwork = db.Table(
    u'content_tracknetwork',
    db.Column(u'track_id', db.ForeignKey('content_track.id')),
    db.Column(u'network_id', db.ForeignKey('radio_network.id'))
)


class ContentTrack(BaseMixin, db.Model):
    """A track to which audio content is added"""
    __tablename__ = u'content_track'

    name = db.Column(db.String(STRING_LEN))
    description = db.Column(db.Text)
    uri = db.Column(db.String(200))
    # add array
    type_id = db.Column(db.ForeignKey('content_type.id'))
    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    deleted = db.Column(db.Boolean, default=False)
    continuous_play = db.Column(db.Boolean)

    content_type = db.relationship(u'ContentType', backref=db.backref('track_content'))
    networks = db.relationship(u'Network', secondary=u'content_tracknetwork', backref=db.backref('tracks'))

    def __unicode__(self):
        return self.name


class ContentUploads(BaseMixin, db.Model):
    """An upload to a particular track"""
    __tablename__ = u'content_uploads'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    ok_to_play = db.Column(db.Boolean)
    order = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=False)

    uploaded_by = db.Column(db.ForeignKey('user_user.id'))
    track_id = db.Column(db.ForeignKey('content_track.id'))
    type_id = db.Column(db.ForeignKey('content_type.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    track = db.relationship(u'ContentTrack', backref=db.backref('files'))

    def __unicode__(self):
        return self.name

    @hybrid_property
    def is_remote(self):
        return self.uri.startswith('http://') or self.uri.startswith('https://')


class CommunityMenu(BaseMixin, db.Model):
    """An IVR menu for communities to record ads, announcements and greetings"""
    __tablename__ = u"content_communitymenu"

    station_id = db.Column(db.ForeignKey('radio_station.id'))
    welcome_message = db.Column(db.String(200))
    welcome_message_txt = db.Column(db.Text())
    no_input_message = db.Column(db.String(200))
    no_input_message_txt = db.Column(db.Text())
    days_prompt = db.Column(db.String(200))
    days_prompt_txt = db.Column(db.Text())
    record_prompt = db.Column(db.String(200))
    record_prompt_txt = db.Column(db.Text())
    message_type_prompt = db.Column(db.String(200))
    message_type_prompt_txt = db.Column(db.Text())
    finalization_prompt = db.Column(db.String(200))
    finalization_prompt_txt = db.Column(db.Text())
    goodbye_message = db.Column(db.String(200))
    goodbye_message_txt = db.Column(db.Text())
    use_tts = db.Column(db.Boolean(), default=False)
    prefetch_tts = db.Column(db.Boolean(), default=True)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    station = db.relationship(u'Station', backref=db.backref('community_menu'))
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class CommunityContent(BaseMixin, db.Model):
    """A message left by a member of the community (ad, greeting, announcement)"""
    __tablename__ = u"content_communitycontent"

    station_id = db.Column(db.ForeignKey('radio_station.id'))
    originator = db.Column(db.String(20))
    message = db.Column(db.String(100))
    duration = db.Column(db.Integer)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    type_code = db.Column(db.Integer)
    valid_until = db.Column(db.DateTime(timezone=True))

    approved = db.Column(db.Boolean(), default=False)
    deleted = db.Column(db.Boolean, default=False)

    station = db.relationship(u'Station', backref=db.backref('community_content'))


class ContentPodcast(BaseMixin, db.Model):
    """Definition of a podcast"""
    __tablename__ = u'content_podcast'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    ok_to_play = db.Column(db.Boolean)
    created_by = db.Column(db.ForeignKey('user_user.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    deleted = db.Column(db.Boolean)


class ContentPodcastDownload(BaseMixin, db.Model):
    """Download of a podcast file"""
    __tablename__ = u'content_podcastdownload'

    file_name = db.Column(db.String(255, convert_unicode=True))
    duration = db.Column(db.String(10))
    title = db.Column(db.String(255, convert_unicode=True))
    summary = db.Column(db.Text(None, convert_unicode=True))
    podcast_id = db.Column(db.ForeignKey('content_podcast.id'))
    date_published = db.Column(db.DateTime(timezone=True))
    date_downloaded = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    podcast = db.relationship(u'ContentPodcast', backref=db.backref('podcast_downloads'))


class ContentMusic(BaseMixin, db.Model):
    """Music files on the phone of a station"""
    __tablename__ = u'content_music'

    title = db.Column(db.String(300, convert_unicode=True))
    album_id = db.Column(db.ForeignKey('content_musicalbum.id'))
    duration = db.Column(db.Integer)
    station_id = db.Column(db.ForeignKey('radio_station.id', ondelete='SET NULL'), nullable=True)
    artist_id = db.Column(db.ForeignKey('content_musicartist.id', ondelete='SET NULL'), nullable=True)
    station = db.relationship(u'Station', backref=db.backref('music'))
    artist = db.relationship(u'ContentMusicArtist', backref=db.backref('music'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())


class ContentMusicAlbum(BaseMixin, db.Model):
    """Albums of Music files on the phone of a station"""
    __tablename__ = u'content_musicalbum'

    title = db.Column(db.String(255, convert_unicode=True))
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    station = db.relationship(u'Station', backref=db.backref('albums'))


class ContentMusicArtist(BaseMixin, db.Model):
    """Artists for the media on phones"""
    __tablename__ = u'content_musicartist'

    title = db.Column(db.String(255, convert_unicode=True))
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    station = db.relationship(u'Station', backref=db.backref('artists'))


class ContentMusicPlaylist(BaseMixin, db.Model):
    """Playlist of the music files on a station"""
    __tablename__ = u'content_musicplaylist'

    title = db.Column(db.String(STRING_LEN))
    station_id = db.Column(db.ForeignKey('radio_station.id'))
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    station = db.relationship(u'Station', backref=db.backref('playlists'))
    deleted = db.Column(db.Boolean)


class ContentMusicPlayListItemType(BaseMixin, db.Model):
    """Type of Items in a playlist mapping to media - """
    __tablename__ = u'content_musicplaylistitemtype'

    title = db.Column(db.String(STRING_LEN))


t_musicartist = db.Table(
    u'content_music_musicartist',
    db.Column(u'music_id', db.ForeignKey('content_music.id')),
    db.Column(u'artist_id', db.ForeignKey('content_musicartist.id'))
)


class ContentMusicPlaylistItem(BaseMixin, db.Model):
    """Definition of an item (song, album, artist) on a playlist"""
    __tablename__ = 'content_musicplaylistitem'
    playlist_id = db.Column(db.ForeignKey('content_musicplaylist.id'))
    playlist_item_id = db.Column(db.Integer)
    playlist_item_type_id = db.Column(db.ForeignKey('content_musicplaylistitemtype.id'))
    updated_at = db.Column(db.DateTime(), server_default=func.now())
    created_at = db.Column(db.DateTime(), server_default=func.now())
    deleted = db.Column(db.Boolean, default=False)


class ContentStream(BaseMixin, db.Model):
    """Definition of a stream"""
    __tablename__ = u'content_stream'

    name = db.Column(db.String(STRING_LEN))
    uri = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    ok_to_play = db.Column(db.Boolean)
    created_by = db.Column(db.ForeignKey('user_user.id'))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    deleted = db.Column(db.Boolean)
