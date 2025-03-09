from app import db
from app.admin import bp
from app.utils import current_agency
from app.models import (
    Agency as AgencyModel,
    Client as ClientModel
)
from flask import url_for, redirect, render_template, request
from flask_login import login_required
# TODO: Add route to view all agencies registered.
# TODO: Add route to view all the clients registered within the agency.


@bp.route("/all-agencies")
@login_required
def all_agencies():
    if not current_agency.is_admin():
        return redirect(url_for('main.home'))
    q = (
        db.select(AgencyModel)
        .where(AgencyModel.id != current_agency.id)
    )
    agencies = db.session.scalars(q).all()
    return render_template("show_all_agency.html", agencies=agencies)


@bp.route("/all-client")
@login_required
def all_clients():
    if not current_agency.is_admin():
        return redirect(url_for('main.home'))
    agency_id = request.args.get("agency_id", 1)
    q = (
        db.select(ClientModel)
        .where(ClientModel.agency_id == agency_id)
    )
    clients = db.session.scalars(q).all()
    return render_template(
        "show_all_client.html",
        clients=clients,
        agency_name=clients[0].agency.name
    )
