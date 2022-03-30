import csv
import datetime

from flask import request, send_file
from flask_appbuilder import BaseView, expose
from sqlalchemy import text

import config
from offers_collector import db, appbuilder


get_report_stmt = text(
    """
        select
            user_offers.username,
            user_offers.type,
            user_offers.payment_method_id,
            user_offers.payment_method,
            user_offers.currency,
            user_offers.cryptocurrency,
            sum(user_offers.duration)
        from (
            select
                of.owner as username,
                pm.name as payment_method,
                pm.id as payment_method_id,
                pm.currency,
                of.cryptocurrency,
                of.type,
                max(of.collection_time::timestamp) - min(of.collection_time::timestamp) as duration
            from offer of
            join payment_method pm on pm.id = of.paymethod_id
            where of.collection_time >= (:start_date) and of.collection_time < (:end_date)
            group by 
                of.owner,
                pm.id,
                of.cryptocurrency,
                of.type,
                of.offer_id
            order by count(of.owner) desc, pm.id
        ) user_offers
        group by
            user_offers.username,
            user_offers.payment_method,
            user_offers.payment_method_id,
            user_offers.currency,
            user_offers.cryptocurrency,
            user_offers.type
    """
)


class OffersReportView(BaseView):
    default_view = 'list'

    _item_map = {
        "sec": 1,
        "min": 60,
        "hour": 60 * 60,
        "day": 60 * 60 * 24
    }

    def _get_report_data(self, start_dt, end_dt):
        return db.engine.execute(get_report_stmt, start_date=start_dt, end_date=end_dt).all()

    @expose(url='/load-csv/', methods=("GET",))
    def send_report(self):
        end_dt = request.args.get("end_dt")
        end_dt = datetime.datetime.fromisoformat(end_dt) if end_dt is not None else datetime.datetime.now().replace(
            second=0, microsecond=0)

        start_dt = request.args.get("start_dt")
        start_dt = datetime.datetime.fromisoformat(start_dt) if start_dt is not None else end_dt - datetime.timedelta(
            days=1)

        duration = int(request.args.get("duration", "28800"))

        result = self._get_report_data(start_dt, end_dt)

        CSV_HEADERS = ("username", "type", "payment_method_id", "payment_method", "currency", "cryptocurrency", "duration")
        csv_data = list(map(lambda x: dict(zip(CSV_HEADERS, x)), filter(lambda x: x[6].seconds >= duration, result)))
        for data in csv_data:
            data['duration'] = data['duration'].seconds
        filename = f"offers_report.csv"
        with open(file=config.BASE_DIR / filename, mode="w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(csv_data)
        return send_file(config.BASE_DIR / filename, attachment_filename=filename)

    @expose(url='/list/', methods=("GET", "POST"))
    def list(self, **kwargs):
        end_dt = datetime.datetime.now().replace(second=0, microsecond=0)
        start_dt = end_dt - datetime.timedelta(days=1)
        duration = 28800
        if request.method == 'POST':
            start_dt = datetime.datetime.fromisoformat(request.form.get("start_dt"))
            end_dt = datetime.datetime.fromisoformat(request.form.get("end_dt"))
            duration = int(request.form.get("duration", duration))

        result = self._get_report_data(start_dt, end_dt)
        CSV_HEADERS = ("username", "type", "payment_method_id", "payment_method", "currency", "cryptocurrency", "duration")
        csv_data = list(map(lambda x: dict(zip(CSV_HEADERS, x)), filter(lambda x: x[6].seconds >= duration, result)))

        for data in csv_data:
            data['duration'] = data['duration'].seconds

        return self.render_template(
            'offer_reports.html',
            items=csv_data,
            start_dt=start_dt.isoformat(),
            end_dt=end_dt.isoformat(),
            duration=duration
        )


appbuilder.add_view(OffersReportView, "offers", category='reports')
