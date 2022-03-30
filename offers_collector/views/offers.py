from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from offers_collector import db, appbuilder
from offers_collector.database.models import Offer


class OfferView(ModelView):
    datamodel = SQLAInterface(Offer)
    label_columns = {
        'offer_id': 'offer id',
        'paymethod_id': 'paymethod id',
        'owner_last_activity': 'owner last activity',
        'is_owner_verificated': 'is owner verificated',
        'collection_time': 'collection time'
    }
    search_columns = ['offer_id', 'type', 'owner', 'currency', 'cryptocurrency', 'paymethod_id', 'collection_time']
    list_columns = [
        'offer_id',
        'rate',
        'type',
        'owner',
        'currency',
        'cryptocurrency',
        'available',
        'paymethod_id',
        'owner_last_activity',
        'is_owner_verificated',
        'collection_time',
    ]


appbuilder.add_view(OfferView, "offers", category='base')
