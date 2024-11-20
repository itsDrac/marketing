from app import db
from app.models import (
    Agency as AgencyModel,
    Client as ClientModel,
    Campaign as CampaignModel,
    Lead as LeadModel,
    BankTransaction as BankTransactionModel,
    MailInvoice as MailInvoiceModel,
    CallRecord as CallRecordModel,
)
from app.mails import MailHelper
from app.calls import CallHelper
from app.client.bank_handler import get_transactions
from app.utils import current_agency, new_transactions
from app.campaign import bp
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date


@bp.route('/<int:camp_id>')
@login_required
def show_campaign(camp_id):
    return render_template(
        "campaign_page.html",
        camp_id=camp_id,
        title="Campaign Page"
        )


@bp.route('/list-leads')
def list_leads():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(LeadModel)
        .join(CampaignModel, CampaignModel.id == LeadModel.campaign_id)
        .join(ClientModel, ClientModel.id == CampaignModel.client_id)
        .join(AgencyModel, AgencyModel.id == ClientModel.agency_id)
        .where(AgencyModel.id == current_agency.id)
        .where(CampaignModel.id == campaign_id)
    )
    leads = db.session.scalars(q).all()
    return render_template(
        "list_leads.html",
        leads=leads,
        camp_id=campaign_id,
        title="Show Leads Page"
        )


@bp.route("/sync-transactions", methods=["PUT"])
def sync_transactions():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(ClientModel, CampaignModel)
        .join(ClientModel, CampaignModel.client_id == ClientModel.id)
        .where(CampaignModel.id == campaign_id)
        .where(ClientModel.agency_id == current_agency.id)
        )
    data = db.session.execute(q).one_or_none()
    if not data:
        return redirect(url_for("campaign.list_leads", camp_id=campaign_id))
    existingClient, existingCampaign = data
    apiData = get_transactions(existingClient, existingCampaign)
    if not apiData:
        flash("Some error came when getting transactions from bank", "danger")
        return redirect(url_for("campaign.list_leads", camp_id=campaign_id))
    newTransactions = new_transactions(apiData.get("transactions"))
    if newTransactions:
        add_bank_transactions(newTransactions, existingCampaign)
        message = "Done! successfuly added new transactions"
    else:
        message = "Checked No New transactions"
    return message


@bp.route("/get-bank-transactions")
def get_bank_transactions():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(BankTransactionModel)
        .join(LeadModel, LeadModel.id == BankTransactionModel.lead_id)
        .where(LeadModel.campaign_id == campaign_id)
    )
    bankTransactions = db.session.scalars(q).all()
    return render_template("get_bank_transactions.html", transactions=bankTransactions)


@bp.route("/get-mail-invoice")
def get_mail_invoices():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(MailInvoiceModel)
        .join(LeadModel, LeadModel.id == MailInvoiceModel.lead_id)
        .where(LeadModel.campaign_id == campaign_id)
    )
    mailInvoices = db.session.scalars(q).all()
    return render_template("get_mail_invoices.html", invoices=mailInvoices)


def add_bank_transactions(transactions, existingCampaign):
    bankTransactions = []
    for transaction in transactions:
        q = (
            db.select(LeadModel)
            .where(LeadModel.fullname.ilike(f"{transaction.get('counterpartName')}%"))
            .where(LeadModel.campaign_id == existingCampaign.id)
            )
        existingLead = db.session.scalar(q)
        if not existingLead:
            continue
        newBankTransaction = BankTransactionModel(
            finapi_id=transaction.get("id"),
            date=date.fromisoformat(transaction.get("bankBookingDate")),
            amount=transaction.get("amount"),
            lead_id=existingLead.id,
            lead=existingLead
        )
        bankTransactions.append(newBankTransaction)

    db.session.add_all(bankTransactions)
    db.session.commit()


@bp.route("/sync-mails", methods=["PUT"])
def sync_mails():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(ClientModel, CampaignModel)
        .join(ClientModel, CampaignModel.client_id == ClientModel.id)
        .where(CampaignModel.id == campaign_id)
        .where(ClientModel.agency_id == current_agency.id)
        )
    data = db.session.execute(q).one_or_none()
    if not data:
        return "No Campaign found"
    existingClient, existingCampaign = data
    helper = MailHelper(existingClient)
    if not helper.check_mail_connection():
        return "Unable to access Mails, Please check email and password"
    mails = helper.get_mails(existingCampaign)
    if not mails:
        return "Checked No new mails"
    data = helper.get_invoice_amount(mails)
    newMailInvoices = []
    for mail, amount in data:
        q = (
            db.select(LeadModel)
            .where(LeadModel.email.in_(mail.to))
            .where(LeadModel.campaign_id == campaign_id)
        )
        existingLead = db.session.scalar(q)
        newMailInvoice = MailInvoiceModel(
            mail_id=mail.uid,
            subject=mail.subject,
            date=mail.date,
            amount=amount,
            lead_id=existingLead.id,
            lead=existingLead
        )
        newMailInvoices.append(newMailInvoice)
    db.session.add_all(newMailInvoices)
    db.session.commit()
    return "mails synced"


@bp.route("/sync-calls", methods=["PUT"])
def sync_calls():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(ClientModel, CampaignModel)
        .join(ClientModel, CampaignModel.client_id == ClientModel.id)
        .where(CampaignModel.id == campaign_id)
        .where(ClientModel.agency_id == current_agency.id)
        )
    data = db.session.execute(q).one_or_none()
    if not data:
        return "No Campaign found"
    existingClient, existingCampaign = data
    helper = CallHelper(existingClient)
    calls = helper.get_calls(existingCampaign)
    calls = helper.filter_calls(calls['calls'], existingCampaign.leads)
    if not calls:
        return "Checked No new calls"
    newCalls = []
    for call in calls:
        q = (
            db.select(LeadModel)
            .where(LeadModel.phone == call['raw_digits'])
            .where(LeadModel.campaign_id == existingCampaign.id)
        )
        existingLead = db.session.scalar(q)
        transaction = helper.get_call_transcription(call)
        from pprint import pprint
        pprint(call)
        # TODO: convert call date(unix date format to python date type)
        newCall = CallRecordModel(
            call_id=call["id"],
            duration=call["duration"],
            date=helper.convert_date(call["started_at"]),
            summary=transaction,
            number=call['raw_digits'],
            direction=call["direction"],
            lead_id=existingLead.id,
            lead=existingLead
        )
        newCalls.append(newCall)
    db.session.add_all(newCalls)
    db.session.commit()
    return "Calls Synced"


@bp.route("/get-call-recording")
def get_call_recording():
    campaign_id = request.args.get("camp_id")
    q = (
        db.select(CallRecordModel)
        .join(LeadModel, LeadModel.id == CallRecordModel.lead_id)
        .where(LeadModel.campaign_id == campaign_id)
    )
    callRecordings = db.session.scalars(q).all()
    return render_template("get_call_recording.html", recordings=callRecordings)
