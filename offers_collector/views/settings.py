from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from offers_collector import db, appbuilder
from offers_collector.database.models import Settings


class SettingsView(ModelView):
    datamodel = SQLAInterface(Settings)
    label_columns = {
        'conf_name': 'conf name',
        'conf_value': 'conf value',
    }
    search_columns = ['conf_name', ]
    list_columns = [
        'conf_name',
        'conf_value',
    ]


appbuilder.add_view(SettingsView, "settings", category='base')
