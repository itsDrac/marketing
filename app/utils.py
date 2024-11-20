from app import db
from app.models import BankTransaction as BankTransactionModel
from flask_login import current_user

current_agency = current_user

email_server_choices = [
    ("None", "Not Selected"),
    ("gmail", "Gamil"),
    ("outlook", "Outlook"),
    ("t-online", "T online"),
    ("web.de", "Web de"),
]


def email_server_value(value):
    if value == 'None':
        return None
    return value


def new_transactions(transactions):
    newTransactions = []
    for transaction in transactions:
        q = (db.select(BankTransactionModel)
             .where(BankTransactionModel.finapi_id == transaction['id']))
        data = db.session.scalar(q)
        if not data:
            newTransactions.append(transaction)
    return newTransactions
