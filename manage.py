# -*- coding: utf-8 -*-

import os
import subprocess
import errno

from flask.ext.script import Manager

from rootio import create_app
from rootio.extensions import db

from rootio.radio import Station, Language
from rootio.user import User, UserDetail, ADMIN, ACTIVE
from rootio.utils import MALE

from alembic import command
from alembic.config import Config


app = create_app()
manager = Manager(app)

alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")

@manager.command
def run():
    """Run in local machine."""

    app.run(debug=True)

@manager.command
def alembic():
    """Run in local machine."""
    subprocess.call(["env/bin/alembic", "init", "alembic"])

@manager.command
def migrate(direction):
    """Migrate db revision"""
    if direction == "up":
        command.upgrade(alembic_config, "head")
    elif direction == "down":
        command.downgrade(alembic_config, "-1")

@manager.command
def migration(message):
    """Create migration file"""
    command.revision(alembic_config, message=message)

@manager.command
def initdb():
    """Init/reset database with default data."""

    db.drop_all()
    db.create_all()

    admin = User(
            name=u'admin',
            email=u'admin@example.com',
            password=u'123456',
            role_code=ADMIN,
            status_code=ACTIVE,
            user_detail=UserDetail(
                gender_code=MALE,
                age=25,
                url=u'http://example.com',
                location=u'Kampala',
                bio=u''))
    db.session.add(admin)
    
    english = Language(name="English",iso639_1="en",iso639_2="eng",locale_code="en_UG")
    db.session.add(english)
    luganda = Language(name="Luganda",iso639_1="lg",iso639_2="lug",locale_code="lg_UG")
    db.session.add(luganda)

    db.session.commit()
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, "head")

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()