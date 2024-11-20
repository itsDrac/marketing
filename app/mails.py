from app import db
from app.models import Lead as LeadModel, MailInvoice as MailInvoiceModel
from imap_tools import MailBox, A, OR
from PyPDF2 import PdfReader
from datetime import date, timedelta
import io
import re

KEYWORDS = [
    "Rechnung",
    "Zahlungsaufforderung",
    "Lieferung und Rechnung",
    "Kosten und Zahlung",
    "Faktura",
    "Kundenauftrag",
    "Liefer und Rechnungsinformationen"
]

PATTERN = r"/(Gesamtbetrag|total)\s+(\d+(?:,\d+)?)"
reg = re.compile(r"(Gesamtbetrag|total|Summe|Rechnungsbetrag|Zahlungsbetrag)\s+(\d+(?:[\.,]\d+)*)")


class MailHelper:
    existingClient = None
    domain = None
    folder = None

    def __init__(self, existingClient):
        self.existingClient = existingClient
        if existingClient.email_server == "gmail":
            self.folder = "[Gmail]/Sent Mail"
            self.domain = "imap.gmail.com"
        elif existingClient.email_server == "outlook":
            self.folder = "Sent"
            self.domain = "imap-mail.outlook.com"
        elif existingClient.email_server == "t-online":
            self.folder = "INBOX.Sent"
            self.domain = "secureimap.t-online.de"
        elif existingClient.email_server == "web.de":
            self.folder = "Gesendet"
            self.domain = "imap.web.de"
        else:
            return False

    def check_mail_connection(self):
        result = None
        try:
            mb = MailBox(self.domain)
            mb.login(self.existingClient.email, self.existingClient.email_password, self.folder)
            result = True
        except Exception:
            result = False
        finally:
            mb.logout()
        return result

    def get_mails(self, existingCampaign):
        with MailBox(self.domain).login(self.existingClient.email, self.existingClient.email_password) as mb:  # noqa E501
            mb.folder.set(self.folder)
            criteria = A(
                OR(subject=KEYWORDS),
                OR(to=[lead.email for lead in existingCampaign.leads]),
                sent_date_gte=existingCampaign.start_date,
                sent_date_lt=(existingCampaign.end_date or date.today()) + timedelta(days=1)
            )
            # TODO: Unable to fetch email with Or condition for subject.
            mails = mb.fetch(criteria, limit=30, reverse=True)
            new_mails = self._get_new_mails(list(mails), existingCampaign)
            return new_mails

    def _get_new_mails(self, mails, existingCampaign):
        new_mails = []
        for mail in mails:
            q = (
                db.select(MailInvoiceModel)
                .where(MailInvoiceModel.mail_id == mail.uid)
                .join(LeadModel, LeadModel.id == MailInvoiceModel.lead_id)
                .where(LeadModel.campaign_id == existingCampaign.id)
            )
            existingMail = db.session.scalar(q)
            if not existingMail:
                new_mails.append(mail)
        return new_mails

    def get_invoice_amount(self, mails):
        data = []
        for mail in mails:
            text = ""
            if mail.attachments:
                text = self.read_attachements(mail.attachments)
            else:
                text = mail.text
            matchs = reg.findall(text, re.IGNORECASE)
            total_amt = 0.00
            print(matchs)
            for _word, amt in matchs:
                total_amt += float(amt.replace(".", "").replace(",", "."))
            print(total_amt)
            data.append((mail, total_amt))
        return data

    def read_attachements(self, attachements):
        text = ""
        for att in attachements:
            if not att.content_type == "application/pdf" and att.filename.endswith(".pdf"):
                continue
            with io.BytesIO(att.payload) as invoice:
                reader = PdfReader(invoice)
                for page in reader.pages:
                    text += page.extract_text()
        return text

    def read_body(self, body):
        # TODO: Read body to check if those are invoice and return the ammount.
        pass
