from app import db, login_manager
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from cryptography.fernet import Fernet
from typing import List, Optional
from datetime import date, datetime
from time import time
import sqlalchemy.orm as so
import sqlalchemy as sa
import base64
import json
import jwt


@login_manager.user_loader
def load_user(userId):
    return db.session.get(Agency, userId)


class Agency(db.Model, UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(50))
    email: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String(256),
                                                init=False, deferred=True)
    clients: so.Mapped[List["Client"]] = so.relationship(
            back_populates="agency", cascade="all, delete", init=False
            )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.email in current_app.config['ADMINS']


# make a Client class
class Client(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    phone: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)
    email_password: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50), init=False)
    email_server: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), init=False)
    bank_username: so.Mapped[str] = so.mapped_column(sa.String(50), init=False)
    bank_password: so.Mapped[str] = so.mapped_column(sa.String(50), init=False)
    bank_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), init=False)
    aircall_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50), init=False)
    aircall_key: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50), init=False)
    agency_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('agency.id'), index=True)
    agency: so.Mapped["Agency"] = so.relationship(back_populates="clients")
    fetch_date: so.Mapped[Optional[date]] = so.mapped_column(sa.Date, default=None, init=False)
    campaigns: so.Mapped[List["Campaign"]] = so.relationship(
            back_populates="client", cascade="all, delete", init=False
            )
    is_bank_connected: so.Mapped[bool] = so.mapped_column(
        sa.Boolean(create_constraint=False),
        default=False, init=False
    )
    # Client class will have one (Agency) to many (Client) connection.
    # Client class will have one (Client) to many (Campaign) connection.

    def add_bank_info(self):
        self.bank_username = f"{self.id}@{self.email}"
        self.bank_password = f"{self.name}@{self.email}"

    @staticmethod
    def verify_client_token(token):
        try:
            client_id = jwt.decode(
                    token, current_app.config["CLIENT_KEY"],
                    algorithms="HS256"
                    )["client_id"]
            return client_id
        except Exception:
            return

    def get_client_token(self, expires_in=1800):
        return jwt.encode(
                {"client_id": self.id, "exp": time() + expires_in},
                current_app.config["CLIENT_KEY"], algorithm="HS256"
            )

    @staticmethod
    def get_encrypted_password(password):
        key = current_app.config["EMAIL_PASSWORD_KEY"]
        f = Fernet(key.encode())
        password = password.encode()
        encrypt_password = f.encrypt(password)
        return encrypt_password.decode("UTF-8")

    def get_decrypted_password(self):
        key = current_app.config["EMAIL_PASSWORD_KEY"]
        f = Fernet(key.encode())
        decrypted_password = f.decrypt(self.email_password)
        return decrypted_password.decode("UTF-8")


class Campaign(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    token: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), init=False)
    client_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('client.id'), index=True)
    client: so.Mapped["Client"] = so.relationship(back_populates="campaigns")
    end_date: so.Mapped[Optional[date]] = so.mapped_column(sa.Date)
    start_date: so.Mapped[date] = so.mapped_column(sa.Date, default=date.today)
    leads: so.Mapped[List["Lead"]] = so.relationship(
            back_populates="campaign", cascade="all, delete", init=False
            )

    def make_token(self):
        strData = json.dumps({
            "campaign_id": self.id,
            "client_id": self.client_id
        })
        byteToken = base64.urlsafe_b64encode(strData.encode("utf-8"))
        self.token = byteToken.decode()

    @staticmethod
    def get_campaign_by_token(token):
        # byteToken = token.encode("utf-8")
        print(token)
        strData = base64.urlsafe_b64decode(token)
        data = json.loads(strData)
        if not data.get("client_id"):
            print("cant find client_id")
            return None
        campaign = db.get_or_404(Campaign, data.get("campaign_id"))
        if not campaign.client_id == int(data.get("client_id")):
            print("Here")
            return None
        return campaign


class Lead(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    fullname: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    phone: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    address: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    campaign_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('campaign.id'), index=True)
    campaign: so.Mapped["Campaign"] = so.relationship(back_populates="leads")
    bank_transactions: so.Mapped[List["BankTransaction"]] = so.relationship(
        back_populates="lead",
        cascade="all, delete",
        init=False
    )
    mail_invoices: so.Mapped[List["MailInvoice"]] = so.relationship(
        back_populates="lead",
        cascade="all, delete",
        init=False
    )
    call_records: so.Mapped[List["CallRecord"]] = so.relationship(
        back_populates="lead",
        cascade="all, delete",
        init=False
    )

    @staticmethod
    def is_registered(email, campaign):
        q = (
            db.select(Lead)
            .where(Lead.email == email)
            .where(Lead.campaign == campaign)
        )
        existingLead = db.session.scalar(q)
        return bool(existingLead)


class BankTransaction(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    finapi_id: so.Mapped[int] = so.mapped_column(sa.BigInteger, nullable=False, index=True)
    date: so.Mapped[date] = so.mapped_column(sa.Date)
    amount: so.Mapped[float] = so.mapped_column(sa.Float(3))
    lead_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('lead.id'), index=True)
    lead: so.Mapped["Lead"] = so.relationship(back_populates="bank_transactions")


class MailInvoice(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    mail_id: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)
    subject: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    date: so.Mapped[date] = so.mapped_column(sa.Date)
    amount: so.Mapped[float] = so.mapped_column(sa.Float(3))
    lead_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('lead.id'), index=True)
    lead: so.Mapped["Lead"] = so.relationship(back_populates="mail_invoices")


class CallRecord(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, init=False)
    call_id: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=False)
    duration: so.Mapped[int] = so.mapped_column(sa.Integer)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    summary: so.Mapped[str] = so.mapped_column(sa.Text)
    number: so.Mapped[str] = so.mapped_column(sa.String(20))
    direction: so.Mapped[str] = so.mapped_column(sa.String(20))
    lead_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('lead.id'), index=True)
    lead: so.Mapped["Lead"] = so.relationship(back_populates="call_records")
    aircall_number: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), default="")
