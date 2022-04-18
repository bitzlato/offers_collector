import logging

from flask_appbuilder.models.decorators import renders
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from offers_collector import db


logger = logging.getLogger(__file__)


class PaymentMethod(db.Model):
    __tablename__ = "payment_method"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(120))
    currency = db.Column(db.String(12), db.ForeignKey('currency.code'))

    def __repr__(self):
        return f"PaymentMethod(id={self.id!r}, name={self.name!r})"


class Currency(db.Model):
    __tablename__ = "currency"

    code = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(120))

    def __repr__(self):
        return f"Currency(code={self.code!r}, name={self.name!r})"


class Cryptocurrency(db.Model):
    __tablename__ = "cryptocurrency"

    code = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(120))

    def __repr__(self):
        return f"Cryptocurrency(code={self.code!r}, name={self.name!r})"


class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    offer_id = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL)
    type = db.Column(db.String(120))
    owner = db.Column(db.String(120))
    currency = db.Column(db.String(12), db.ForeignKey('currency.code'))
    cryptocurrency = db.Column(db.String(12), db.ForeignKey('cryptocurrency.code'))
    available = db.Column(db.Boolean)
    paymethod_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'))
    paymethod = relationship("PaymentMethod")
    owner_last_activity = db.Column(db.BigInteger)
    is_owner_verificated = db.Column(db.Boolean)
    collection_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
    raw_data = db.Column(JSONB())

    def __repr__(self):
        return f"Offer(id={self.id!r}, offer_id={self.offer_id!r}, currency={self.currency!r}, cryptocurrency={self.cryptocurrency!r})"


class Settings(db.Model):
    __tablename__ = "setting"

    conf_name = db.Column(db.String(150), nullable=False, unique=True, primary_key=True)
    conf_value = db.Column(db.String, nullable=False)

    @staticmethod
    def set_configuration_default_value(name: str, value: str):
        try:
            db.session.add(Settings(conf_name=name, conf_value=value))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.info(f"Key {name} already exists")
