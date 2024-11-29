from app import db
from app.models import (
    Lead as LeadModel,
    BankTransaction as BankTransactionModel,
    CallRecord as CallRecordModel,
    MailInvoice as MailInvoiceModel
)
import io
import csv


class ReportHelper:
    #  Add functionality to download Lead report of a campaign.
    # Add functionality to download bank transactions report of a campaign.
    # TODO: Add functionality to download MailInvoice report of a campaign.
    # Add functionality to download CallRecord report of a campaign.
    existingCampaign = None

    def __init__(self, existingCampaign):
        self.existingCampaign = existingCampaign

    def lead_report(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Lead Id",
            "Full Name",
            "Phone Number",
            "Email",
            "Address",
        ])
        leads = db.session.scalars(
            db.select(LeadModel).where(
                LeadModel.campaign_id == self.existingCampaign.id
            )
        ).all()
        writer.writerows([
            [lead.id, lead.fullname, lead.phone, lead.email, lead.address] for lead in leads
        ])
        return output

    def bank_report(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Lead Id",
            "Full Name",
            "Email",
            "Phone Number",
            "Bank Transaction Id",
            "Bank Transaction Date",
            "Bank Transaction Amount",
        ])
        transactions = db.session.scalars(
            db.select(BankTransactionModel)
            .join(LeadModel, LeadModel.id == BankTransactionModel.lead_id)
            .where(LeadModel.campaign_id == self.existingCampaign.id)
        ).all()
        writer.writerows([
            [
                bank.lead.id,
                bank.lead.fullname,
                bank.lead.email,
                bank.lead.phone,
                bank.id,
                bank.date,
                bank.amount
            ] for bank in transactions
        ])
        return output

    def call_report(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Lead Id",
            "Full Name",
            "Email",
            "Phone Number",
            "Call Id",
            "Call Date",
            "Call Duration",
            "Call Number",
            "Call Direction",
            "Call Transcription",
        ])
        records = db.session.scalars(
            db.select(CallRecordModel)
            .join(LeadModel, LeadModel.id == CallRecordModel.lead_id)
            .where(LeadModel.campaign_id == self.existingCampaign.id)
        ).all()
        writer.writerows([
            [
                call.lead.id,
                call.lead.fullname,
                call.lead.email,
                call.lead.phone,
                call.id,
                call.date,
                call.duration,
                call.number,
                call.direction,
                call.summary
            ] for call in records
        ])
        return output

    def mail_report(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Lead Id",
            "Full Name",
            "Email",
            "Phone Number",
            "Mail Id",
            "Mail Date",
            "Mail Subject",
            "Mail Amount"
        ])
        records = db.session.scalars(
            db.select(MailInvoiceModel)
            .join(LeadModel, LeadModel.id == MailInvoiceModel.lead_id)
            .where(LeadModel.campaign_id == self.existingCampaign.id)
        ).all()
        writer.writerows([
            [
                mail.lead.id,
                mail.lead.fullname,
                mail.lead.email,
                mail.lead.phone,
                mail.id,
                mail.date,
                mail.subject,
                mail.amount
            ] for mail in records
        ])
        return output
