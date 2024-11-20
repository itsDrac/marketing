from app import db
from app.client import bp
from app.client.bank_handler import get_webform_link, delete_user
from app.client.forms import ClientEditForm
from app.campaign.forms import CampaignForm
from app.models import Client as ClientModel, Campaign as CampaignModel
from app.utils import current_agency, email_server_choices
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required


@bp.route('/list-campaigns', methods=["GET", "POST"])
@login_required
def list_campaigns():
    print(request.method)
    # TODO: Fix bug when form throw error it should not return client_page.html
    client_id = request.args.get("client_id")
    current_client = db.get_or_404(ClientModel, client_id)
    if current_client not in current_agency.clients:
        flash("Client does not exist", "danger")
        # TODO: return 404 error and render custome 404 error page.
        return redirect(url_for('agency.list_clients'))

    form = CampaignForm()
    if form.validate_on_submit():
        print(form.data)
        newCampaign = CampaignModel(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            client_id=client_id,
            client=current_client
        )
        db.session.add(newCampaign)
        db.session.commit()
        newCampaign.make_token()
        db.session.commit()
        return render_template("get_campaign.html", campaign=newCampaign)
    return render_template(
        "client_page.html",
        title="Clients page",
        client=current_client,
        campaigns=current_client.campaigns,
        form=form
    ), 200 if request.method == "GET" else 401


@bp.route("delete-client", methods=["DELETE"])
def delete_client():
    headers = {
        "HX-Refresh": "true"
    }
    client_id = request.args.get("client_id")
    q = (
        db.select(ClientModel)
        .where(ClientModel.id == int(client_id))
        .where(ClientModel.agency == current_agency)
    )
    existingClient = db.session.scalar(q)
    if not existingClient:
        flash("Client does not exisit", "info")
        return "client does not exisit", headers
    if not delete_user(existingClient):
        flash("Unable to delete user", "warning")
        return "unable to delete user", headers
    db.session.delete(existingClient)
    db.session.commit()
    flash("Client deleted", "danger")
    return "Client deleted."


@bp.route("/edit-client", methods=["GET", "POST"])
def edit_client():
    client_id = request.args.get("client_id")
    q = (
        db.select(ClientModel)
        .where(ClientModel.id == int(client_id))
        .where(ClientModel.agency == current_agency)
    )
    existingClient = db.session.scalar(q)
    form = ClientEditForm(originalemail=existingClient.email)
    form.email_server.choices = email_server_choices
    if form.validate_on_submit():
        existingClient.name = form.name.data
        existingClient.email = form.email.data.lower()
        existingClient.phone = form.phone.data
        existingClient.email_password = form.email_password.data
        existingClient.email_server = form.email_server.data
        existingClient.aircall_id = form.aircall_id.data
        existingClient.aircall_key = form.aircall_key.data
        db.session.commit()
        print(existingClient)
        return redirect(url_for('agency.list_clients'))
    form.pre_fill_data(existingClient)
    return render_template(
        "edit_client.html",
        title="Edit Client page",
        existingClient=existingClient,
        form=form
    )


@bp.route("connect-bank", methods=["PUT"])
@login_required
def connect_bank():
    client_id = request.args.get("client_id")
    q = (
        db.select(ClientModel)
        .where(ClientModel.id == int(client_id))
        .where(ClientModel.agency == current_agency)
    )
    existingClient = db.session.scalar(q)
    if not existingClient:
        flash("Client not found", "secondary")
        return redirect(url_for("client.list_campaigns"))
    if existingClient.is_bank_connected:
        flash("Client's bank account is already connected.", "success")
        return redirect(url_for("client.list_campaigns"))
    data = get_webform_link(existingClient)
    if data:
        existingClient.bank_form = data.get("id")
        db.session.commit()
        return render_template("bank_webform_link.html", link=data.get("url"))
    flash("Something went wrong", "danger")
    return redirect(url_for("client.list_campaigns"))


@bp.route("bank-form-connected", methods=["POST"])
def bank_form_connected():
    print("This is called")
    data = request.json
    q = (
        db.select(ClientModel).
        where(ClientModel.bank_form == data.get("webFormId"))
    )
    existingClient = db.session.scalar(q)
    if not existingClient:
        return "Nothing found."
    if data.get("status") == "COMPLETED":
        existingClient.is_bank_connected = True
        db.session.commit()
    return "Done."
