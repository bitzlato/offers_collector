import os

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from sqlalchemy.exc import IntegrityError

import config
from setup_logger import setup_logging

setup_logging(is_debug=config.IS_DEBUG)

db = SQLA()
appbuilder = AppBuilder()


def create_app(conf="config", init_appbuilder: bool = True):
    app = Flask(__name__, template_folder=config.BASE_DIR / 'templates')
    app.config.from_object(conf)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = 'super secret key'
    db.app = app
    db.init_app(app)

    try:
        db.create_all()
    except IntegrityError:
        pass

    from offers_collector.database.models import Settings
    Settings.set_configuration_default_value(name="MAX_OFFER_COUNT", value=os.environ.get('MAX_OFFER_COUNT', '3'))
    Settings.set_configuration_default_value(name="COLLECTOR_CRON_SECONDS", value=os.environ.get('COLLECTOR_CRON_SECONDS', '300'))

    if init_appbuilder is True:
        appbuilder.init_app(app, db.session)

        from .views import OffersReportView, OfferView, SettingsView
    return app

