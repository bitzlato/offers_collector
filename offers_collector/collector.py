import datetime
import time
import logging

import asyncio
from decimal import Decimal
from typing import Dict, List

from aiohttp import ClientSession


import config
import requests

from sqlalchemy import select

from offers_collector.auth import BitzlatoAuthV1
from offers_collector.database.models import db, Currency, Cryptocurrency, PaymentMethod, Offer


logger = logging.getLogger(__file__)


class Collector:
    def __init__(self):
        self.auth = BitzlatoAuthV1(key_=config.API_KEY, email=config.ACCOUNT_EMAIL, kid=config.API_KEY_ID)

    def collect_payment_methods(self):
        start_time = time.time()
        logger.info(f"start collect currencies")

        url = 'https://bitzlato.com/api2/p2p/public/refs/paymethods'

        try:
            data = requests.get(url, headers=self.auth.get_headers()).json()
            known_payment_methods = db.session.execute(select(PaymentMethod.id)).scalars().all()
            payment_methods = list(map(lambda x: PaymentMethod(id=x['id'], name=x['description'], currency=x['currency']), filter(lambda x: x['id'] not in known_payment_methods, data)))
            db.session.bulk_save_objects(payment_methods)
            db.session.commit()
        except Exception as e:
            logger.error(f"failed fetch payment_methods by url {url}", exc_info=e)
            return
        logger.info(f"finish collect payment methods [{time.time() - start_time}]")

    def collect_currencies(self):
        start_time = time.time()
        logger.info(f"start collect currencies")
        url = 'https://bitzlato.com/api/p2p/public/refs/currencies'

        try:
            data = requests.get(url, headers=self.auth.get_headers()).json()
            known_currency_symbols = db.session.execute(select(Currency.code)).scalars().all()
            currencies = list(map(lambda x: Currency(code=x['code'], name=x['name']), filter(lambda x: x['code'] not in known_currency_symbols, data)))
            db.session.bulk_save_objects(currencies)
            db.session.commit()
        except Exception as e:
            logger.error(f"failed fetch currencies by url {url}", exc_info=e)
            return
        logger.info(f"finish collect currencies [{time.time() - start_time}]")

    def collect_cryptocurrencies(self):
        start_time = time.time()
        logger.info(f"start collect cryptocurrencies")
        url = 'https://bitzlato.com/api/p2p/public/refs/cryptocurrencies'

        try:
            data = requests.get(url, headers=self.auth.get_headers()).json()
            known_cryptocurrency_symbols = db.session.execute(select(Cryptocurrency.code)).scalars().all()
            cryptocurrency = list(map(lambda x: Cryptocurrency(code=x['code'], name=x['name']), filter(lambda x: x['code'] not in known_cryptocurrency_symbols, data)))
            db.session.bulk_save_objects(cryptocurrency)
            db.session.commit()
        except Exception as e:
            logger.error(f"failed fetch cryptocurrency by url {url}", exc_info=e)
            return
        logger.info(f"finish collect cryptocurrencies [{time.time() - start_time}]")

    def start(self):
        while True:
            start = datetime.datetime.now()
            s0 = time.time()
            logger.info(f"[{datetime.datetime.now()}] Start collect data!")

            self.collect_cryptocurrencies()
            self.collect_currencies()
            self.collect_payment_methods()

            self.collect_offers()

            logger.info(f"[{datetime.datetime.now()}] Finish collect data! [{time.time() - s0}]")
            sleep_time = config.COLLECTOR_CRON_SECONDS - (datetime.datetime.now() - start).seconds
            time.sleep(sleep_time if sleep_time > 0 else 0)

    async def fetch(self, url, session: ClientSession):
        logger.debug(f"make request for url {url}")
        async with session.get(url, headers=self.auth.get_headers()) as response:
            try:
                if response.ok:
                    return await response.json()
                else:
                    logger.warning(f"failed request {url} with status {response.status}")
                    return {'total': 0, 'data': []}
            except Exception as e:
                logger.error(f"failed fetch {url}", exc_info=e)
                return {'total': 0, 'data': []}

    async def bound_fetch(self, sem, url, session):
        async with sem:
            return await self.fetch(url, session)

    async def _collect_offers(self, limit, skip):
        sem = asyncio.Semaphore(1000)
        url = 'https://bitzlato.com/api/p2p/exchange/dsa/?limit={limit}&skip={skip}&currency={currency}&cryptocurrency={cryptocurrency}&type={type}&paymethod={paymethod}'

        known_cryptocurrency_symbols = db.session.execute(select(Cryptocurrency.code)).scalars().all()
        known_payment_methods = db.session.execute(select(PaymentMethod.id, PaymentMethod.currency)).all()

        urls = []
        for cryptocurrency in known_cryptocurrency_symbols:
            for paymethod in known_payment_methods:
                urls.append(url.format(limit=limit, skip=skip, paymethod=paymethod[0], currency=paymethod[1], cryptocurrency=cryptocurrency, type="purchase"))
                urls.append(url.format(limit=limit, skip=skip, paymethod=paymethod[0], currency=paymethod[1], cryptocurrency=cryptocurrency, type="selling"))

        async with ClientSession() as session:
            tasks = list(map(lambda u: asyncio.ensure_future(self.bound_fetch(sem, u, session)), urls))
            responses = asyncio.gather(*tasks)
            return await responses

    def _add_offers(self, offers: List[Dict]):
        db.session.bulk_save_objects(
            list(map(lambda x: Offer(
                offer_id=x['id'],
                rate=Decimal(x['rate']),
                type=x['type'],
                owner=x['owner'],
                currency=x['currency'],
                cryptocurrency=x['cryptocurrency'],
                available=x['available'],
                paymethod_id=x['paymethodId'],
                owner_last_activity=x['ownerLastActivity'],
                is_owner_verificated=x['isOwnerVerificated'],
                raw_data=x
            ), offers))
        )
        db.session.commit()

    def _filter_offers(self, offers: List):
        filtered_offers = []

        payment_methods = db.session.execute(select(PaymentMethod.id)).scalars().all()
        crypto_currencies = db.session.execute(select(Cryptocurrency.code)).scalars().all()

        for crypto_currency in crypto_currencies:
            for pay_method_id in payment_methods:
                _offers = list(filter(lambda x: x['paymethodId'] == pay_method_id and x['cryptocurrency'] == crypto_currency, offers))
                if len(_offers) > 5:
                    continue
                filtered_offers += _offers
        return filtered_offers

    def collect_offers(self):
        start_time = time.time()
        logger.info(f"start collect offers")

        loop = asyncio.get_event_loop()

        future = asyncio.ensure_future(self._collect_offers(limit=10000, skip=0))
        loop.run_until_complete(future)

        results = future.result()
        results = map(lambda x: x['data'], filter(lambda x: 0 < x['total'] <= config.MAX_OFFER_COUNT, results))
        offers = []
        for _offers in results:
            offers += _offers
        filtered_offers = self._filter_offers(offers=offers)

        self._add_offers(filtered_offers)
        logger.info(f"finish collect offers [{time.time() - start_time}]")
