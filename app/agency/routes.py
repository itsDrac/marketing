from app import db
from app.agency import bp
from app.utils import current_agency, email_server_choices
from app.agency.forms import LoginForm, RegisterForm
from app.client.forms import ClientForm
from app.client.bank_handler import create_customer
from app.models import Agency as AgencyModel, Client as ClientModel
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, logout_user, login_user
from urllib.parse import urlsplit


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        q = db.select(AgencyModel).where(AgencyModel.email == form.email.data.lower())
        existingAgency = db.session.scalar(q)
        if not existingAgency.check_password(form.password.data):
            flash("Incorrect password.", "danger")
            return redirect(url_for("agency.login"))
        login_user(existingAgency, remember=form.remember.data)
        nextPage = request.args.get('next')
        if not nextPage or urlsplit(nextPage).netloc != '':
            nextPage = url_for('agency.list_clients')
        flash(f"Agency {existingAgency.name} Loggedin.", "success")
        return redirect(nextPage)
    return render_template("login.html",
                           form=form,
                           title="Login Page"
                           )


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        newAgency = AgencyModel(
            name=form.name.data,
            email=form.email.data.lower(),
        )
        newAgency.set_password(form.confirm.data)
        db.session.add(newAgency)
        db.session.commit()
        flash(f"Agency {newAgency.name} registered.", "success")
        return redirect(url_for("agency.login"))
    return render_template("register.html",
                           form=form,
                           title="Register Page"
                           )


@bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("agency.register"))


@bp.route("/list-clients", methods=["GET", "POST"])
@login_required
def list_clients():
    headers = {}
    form = ClientForm()
    form.email_server.choices = email_server_choices
    if form.validate_on_submit():
        newClient = ClientModel(
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            agency_id=current_agency.id,
            agency=current_agency
            )
        if form.email_password.data:
            newClient.email_password = form.email_password.data
        if form.email_server.data:
            newClient.email_server = form.email_server.data
        if form.aircall_id.data:
            newClient.aircall_id = form.aircall_id.data
        if form.aircall_key.data:
            newClient.aircall_key = form.aircall_key.data
        newClient.add_bank_info()
        db.session.add(newClient)
        db.session.commit()
        create_customer(newClient)
        return render_template("get_client.html", client=newClient)
    else:
        headers = {
            "HX-Retarget": "#add-client-form",
            "HX-Reselect": "#add-client-form",
            "HX-Reswap": "outerHTML"
        }
    q = (
        db.select(ClientModel)
        .where(ClientModel.agency_id == current_agency.id)
        .order_by(ClientModel.id.desc())
    )
    clients = db.session.scalars(q).all()
    return render_template("agency_page.html",
                           title="Agency dashboard",
                           clients=clients,
                           form=form
                           ), headers
