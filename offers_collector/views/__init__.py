from flask import render_template

from .offers_report import OffersReportView
from .offers import OfferView
from offers_collector import appbuilder


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


__all__ = [
    'OffersReportView',
    'OfferView',
]
