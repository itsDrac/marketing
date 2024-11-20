from app import db
from app.models import (
    Agency as AgencyModel,
    Client as ClientModel,
    Campaign as CampaignModel,
    Lead as LeadModel,
    CallRecord as CallRecordModel,
)
from app.lead import bp
from app.utils import current_agency
from flask import url_for, request
from flask_login import login_required


@bp.route("/add-lead", methods=["GET", "POST"])
def add_lead():
    if request.method == "POST":
        campaignToken = request.headers.get("Campaign-Token")
        if not campaignToken:
            return "No token found", 403
        existingCampaign = CampaignModel.get_campaign_by_token(campaignToken)
        if LeadModel.is_registered(request.json.get("email"), existingCampaign):
            return "Lead already registered", 401
        newLead = LeadModel(
            fullname=request.json.get("fullname", "").strip().lower(),
            phone=request.json.get("phone"),
            email=request.json.get("email"),
            address=request.json.get("address"),
            campaign_id=existingCampaign.id,
            campaign=existingCampaign
        )
        db.session.add(newLead)
        db.session.commit()
    return url_for('lead.add_lead', _external=True)


@bp.route("get-transcription", methods=["PUT"])
@login_required
def get_transcription():
    tran_id = request.args.get("tran_id", 0)
    if not tran_id:
        return "No transcription provided"
    print(current_agency.id)
    q = (
        db.select(CallRecordModel).
        where(CallRecordModel.id == tran_id)
        .join(LeadModel, LeadModel.id == CallRecordModel.lead_id)
        .join(CampaignModel, CampaignModel.id == LeadModel.campaign_id)
        .join(ClientModel, ClientModel.id == CampaignModel.client_id)
        .join(AgencyModel, AgencyModel.id == ClientModel.agency_id)
        .where(AgencyModel.id == current_agency.id)
    )
    existingCall = db.session.scalar(q)
    if not existingCall:
        return "No transcription found."
    return existingCall.summary
