# TODO add username
# TODO уникальность почты
# TODO уникальночсть ника
# TODO Ник только англ


from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_security import SQLAlchemyUserDatastore, Security, login_required, current_user
from flask_security.utils import hash_password
from sqlalchemy import or_, and_
from sqlalchemy.sql import func

from forms.check_form import CheckForm
from forms.debt_form import DebtForm
from forms.event_form import EventForm
from forms.person_form import PersonForm
from forms.repay_form import RepayForm
from forms.event_union_form import EventUnionForm

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:01200120@localhost/debt_manager'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://vwgdncthqvrfxu:" \
                                        "4e44983fca331d02098c0208b79b45579ec69a15c7085765e6fae7e994d864c8@" \
                                        "ec2-34-233-226-84.compute-1.amazonaws.com:5432/d4b55fh4te2e3h"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_RECOVERABLE'] = True

app.secret_key = 'key'

app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['USER_EMAIL_SENDER_EMAIL'] = "noreply@example.com"

from dao.model import *

user_datastore = SQLAlchemyUserDatastore(db, OrmUser, OrmRole)
security = Security(app, user_datastore)


@app.route('/new')
# @roles_accepted("Admin")
def new():
    # role_user = OrmRole(name="User")
    # role_admin = OrmRole(name="Admin")
    # db.session.add_all([role_user, role_admin])
    # db.session.commit()
    #
    # return redirect(url_for('security.login'))

    items_id = db.session.query(OrmCheck.id).filter(OrmCheck.event_id == 20).all()

    for i in items_id:
        pay = OrmPay(
            check_id=i,
            person_id=1,
            sum=0
        )
        db.session.add(pay)
    db.session.commit()

    return redirect(url_for('checks'))


@app.route('/', methods=['GET', 'POST'])
def root():
    # return redirect(url_for('security.login'))
    return render_template('index.html')


@app.route('/person', methods=['GET'])
@login_required
def person():
    result = db.session.query(OrmUser).filter(OrmUser.id == current_user.id).all()

    repay = db.session.query(OrmRepay.sum, OrmRepay.id, OrmEvent.name, OrmUser.name, OrmUser.surname).join(OrmUser,
                                                                                                           OrmUser.id == OrmRepay.id_debt). \
        join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
        filter(and_(OrmRepay.id_repay == current_user.id, OrmRepay.active == False)).all()

    pay_by_category = \
        db.session.query(OrmEvent.id.label("id"), OrmEvent.name.label("name"), OrmEvent.date.label("date"), func.coalesce(func.sum(OrmPay.sum), 0).label("sum")). \
            join(OrmParticipant, OrmParticipant.c.event_id == OrmEvent.id). \
            join(OrmUser, OrmUser.id == OrmParticipant.c.person_id). \
            join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
            outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_id, OrmParticipant.c.person_id == OrmPay.person_id)). \
            filter(OrmUser.id == current_user.id). \
            group_by(OrmEvent.name, OrmEvent.date, OrmEvent.id)

    sub_debt = db.session.query(func.avg(OrmItem.cost).label("costs"), func.sum(OrmDebt.sum).label("sums"),
                                OrmItem.id.label("id")). \
        join(OrmItem, OrmItem.id == OrmDebt.item_id). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        group_by(OrmItem.id).subquery()

    debt_by_category = \
        db.session.query(OrmEvent.id.label("id"), OrmEvent.name.label("name"), OrmEvent.date.label("date"),
                         func.sum(-sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)).label("sum")). \
            join(OrmParticipant, OrmParticipant.c.event_id == OrmEvent.id). \
            join(OrmUser, OrmUser.id == OrmParticipant.c.person_id). \
            join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
            join(OrmItem, OrmItem.check_id == OrmCheck.id). \
            outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
            filter(and_(OrmUser.id == current_user.id, sub_debt.c.id == OrmItem.id)). \
            group_by(OrmEvent.name, OrmEvent.date, OrmEvent.id)

    repay_by_category = db.session.query(OrmEvent.id.label("id"), OrmEvent.name.label("name"), OrmEvent.date.label("date"), func.sum(-OrmRepay.sum).label("sum")).\
        join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
        join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
        filter(and_(OrmRepay.id_repay == current_user.id, OrmRepay.active == True)). \
        group_by(OrmEvent.name, OrmEvent.date, OrmEvent.id)

    redebt_by_category = db.session.query(OrmEvent.id.label("id"), OrmEvent.name.label("name"), OrmEvent.date.label("date"), func.sum(OrmRepay.sum).label("sum")). \
        join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
        join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
        filter(and_(OrmRepay.id_debt == current_user.id, OrmRepay.active == True)). \
        group_by(OrmEvent.name, OrmEvent.date, OrmEvent.id)


    unions = pay_by_category.union(debt_by_category.union(repay_by_category.union(redebt_by_category))).subquery()
    res = db.session.query(unions.c.id, unions.c.name, unions.c.date, func.sum(unions.c.sum).label("sum")).\
        group_by(unions.c.name, unions.c.date, unions.c.id).\
        order_by(unions.c.date.desc()).all()

    i_debt = []
    me_debt = []

    for i in res:
        if i.sum < -1:
            i_debt.append(i)
        elif i.sum > 1:
            me_debt.append(i)

    return render_template('person.html', persons=result, i_debt=i_debt, me_debt=me_debt, repay=repay)


@app.route('/new_person', methods=['GET', 'POST'])
def new_person():
    form = PersonForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('person_form.html', form=form, form_name="New person", action="new_person")
        else:
            new_person = user_datastore.create_user(
                email=form.person_email.data,
                username=form.person_username.data,
                password=form.person_password.data,
                name=form.person_name.data,
                surname=form.person_surname.data,
                card=form.person_card.data,
            )

            role = db.session.query(OrmRole).filter(OrmRole.name == "User").one()

            new_person.roles.append(role)

            db.session.add(new_person)
            db.session.commit()

            return redirect(url_for('security.login'))

    return render_template('person_form.html', form=form, form_name="New person", action="new_person")


# @app.route('/reset_password', methods=['GET', 'POST'])
# def reset_password():
#     form = PersonForm()
#
#     if request.method == 'POST':
#         if not form.validate():
#             return render_template('person_form.html', form=form, form_name="New person", action="new_person")
#         else:
#             new_person = user_datastore.create_user(
#                 email=form.person_email.data,
#                 username=form.person_username.data,
#                 password=form.person_password.data,
#                 name=form.person_name.data,
#                 surname=form.person_surname.data,
#                 card=form.person_card.data,
#             )
#
#             role = db.session.query(OrmRole).filter(OrmRole.name == "User").one()
#
#             new_person.roles.append(role)
#
#             db.session.add(new_person)
#             db.session.commit()
#
#             return redirect(url_for('security.login'))
#
#     return render_template('person_form.html', form=form, form_name="New person", action="new_person")



@app.route('/edit_person', methods=['GET', 'POST'])
@login_required
def edit_person():
    form = PersonForm()

    if request.method == 'GET':

        person_id = request.args.get('person_id')
        person = db.session.query(OrmUser).filter(OrmUser.id == person_id).one()

        form.person_id.data = person_id
        form.person_username.data = person.username
        form.person_email.data = person.email
        form.person_password.data = person.password
        form.person_name.data = person.name
        form.person_surname.data = person.surname
        form.person_card.data = person.card

        return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")


    else:

        if not form.validate():
            return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")
        else:
            person = db.session.query(OrmUser).filter(OrmUser.id == form.person_id.data).one()

            person.email = form.person_email.data
            person.username = form.person_username.data,
            person.password = hash_password(form.person_password.data)
            person.name = form.person_name.data
            person.surname = form.person_surname.data
            person.card = form.person_card.data

            db.session.commit()

            return redirect(url_for('person'))


@app.route('/delete_person', methods=['POST'])
@login_required
def delete_person():
    person_id = request.form['person_id']

    result = db.session.query(OrmUser).filter(OrmUser.id == person_id).one()

    db.session.delete(result)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/friends', methods=['GET'])
@login_required
# @roles_accepted(str(current_user.id))
def friends():
    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_f == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    except_all = all_0.except_(all_1).with_entities("col_1")
    result_friends = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    return render_template('friends.html', persons=result_request, friends=result_friends)


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    person_id = request.form['person_id']

    dell = Orm_Friend.delete().where(or_(and_(Orm_Friend.c.id_o == current_user.id, Orm_Friend.c.id_f == person_id),
                                         and_(Orm_Friend.c.id_f == current_user.id, Orm_Friend.c.id_o == person_id)))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/except_friend', methods=['POST'])
@login_required
def except_friend():
    person_id = request.form['person_id']

    insert = Orm_Friend.insert().values(id_o=current_user.id, id_f=person_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/deny_friend', methods=['POST'])
@login_required
def deny_friend():
    person_id = request.form['person_id']

    dell = Orm_Friend.delete().where(and_(Orm_Friend.c.id_f == current_user.id, Orm_Friend.c.id_o == person_id))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/add_fiend', methods=['POST'])
@login_required
def add_fiend():
    person_id = request.form.get('username')

    frienf_id = db.session.query(OrmUser.id).filter(OrmUser.username == person_id).one()

    insert = Orm_Friend.insert().values(id_o=current_user.id, id_f=frienf_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('friends'))


@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    form = EventUnionForm()

    result = db.session.query(OrmEvent).join(OrmParticipant).filter(
        and_(OrmEvent.id == OrmParticipant.c.event_id, OrmParticipant.c.person_id == current_user.id)). \
        order_by(OrmEvent.date.desc()).all()

    return render_template('event.html', events=result, form=form, action="detail_event")


@app.route('/detail_event', methods=['GET', 'POST'])
@login_required
def detail_event():
    events_id = request.args.get('event_id')

    if events_id != "0":
        event_name = db.session.query(OrmEvent.name). \
            filter(OrmEvent.id == events_id).one()

        participant_id = \
            db.session.query(OrmUser.id, OrmUser.name). \
                join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                filter(OrmEvent.id == events_id). \
                order_by(OrmUser.id).all()

        pay_info = \
            db.session.query(func.coalesce(func.sum(OrmPay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
                outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_id, OrmParticipant.c.person_id == OrmPay.person_id)). \
                filter(OrmCheck.event_id == events_id). \
                group_by(OrmParticipant.c.person_id).order_by(OrmParticipant.c.person_id).all()

        sub_debt = db.session.query(func.avg(OrmItem.cost).label("costs"), func.sum(OrmDebt.sum).label("sums"),
                                    OrmItem.id.label("id")). \
            join(OrmItem, OrmItem.id == OrmDebt.item_id). \
            join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
            filter(OrmCheck.event_id == events_id). \
            group_by(OrmItem.id).subquery()

        categorical_debt = \
            db.session.query(func.sum(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)),
                             OrmParticipant.c.person_id, OrmItem.category). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
                join(OrmItem, OrmItem.check_id == OrmCheck.id). \
                outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
                filter(and_(OrmParticipant.c.event_id == events_id, sub_debt.c.id == OrmItem.id)). \
                group_by(OrmParticipant.c.person_id, OrmItem.category). \
                order_by(OrmParticipant.c.person_id, OrmItem.category).all()

        all_debt = \
            db.session.query(func.sum(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)),
                             OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
                join(OrmItem, OrmItem.check_id == OrmCheck.id). \
                outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
                filter(and_(OrmParticipant.c.event_id == events_id, sub_debt.c.id == OrmItem.id)). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id).all()

        categories = \
            db.session.query(OrmItem.category). \
                join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
                group_by(OrmItem.category).order_by(OrmItem.category).all()

        who_repay = \
            db.session.query(func.coalesce(func.sum(OrmRepay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                outerjoin(OrmRepay, and_(OrmRepay.id_event == OrmEvent.id, OrmRepay.id_debt == OrmParticipant.c.person_id,
                                         OrmRepay.active == True)). \
                filter(OrmEvent.id == events_id). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id)

        whom_repay = \
            db.session.query(func.coalesce(func.sum(OrmRepay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                outerjoin(OrmRepay, and_(OrmRepay.id_event == OrmEvent.id, OrmRepay.id_repay == OrmParticipant.c.person_id,
                                         OrmRepay.active == True)). \
                filter(OrmEvent.id == events_id). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id)

        repay = db.session.query(OrmRepay.sum, OrmRepay.id, OrmEvent.name, OrmUser.name, OrmUser.surname). \
            join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
            join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
            filter(and_(OrmRepay.id_repay == current_user.id, OrmRepay.active == False,
                        OrmRepay.id_event == events_id)).all()

        subquery1 = db.session.query(OrmRepay.id_debt.label("debt"), OrmRepay.id_repay.label("id"),
                                     OrmRepay.sum.label("sum"), OrmUser.name.label("name1"),
                                     OrmUser.surname.label("surname1")). \
            join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
            join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
            filter(and_(OrmRepay.active == True, OrmEvent.id == events_id)).subquery()

        repay_all = db.session.query(subquery1.c.sum.label("sum"), OrmUser.name.label("name2"),
                                     OrmUser.surname.label("surname2"), subquery1.c.name1.label("name1"),
                                     subquery1.c.surname1.label("surname1")).join(OrmUser,
                                                                                  OrmUser.id == subquery1.c.id).order_by(
            subquery1.c.debt).all()

    else:
        form = EventUnionForm()
        if request.method == "POST":
            result = db.session.query(OrmEvent).join(OrmParticipant).filter(
                and_(OrmEvent.id == OrmParticipant.c.event_id, OrmParticipant.c.person_id == current_user.id)). \
                order_by(OrmEvent.date.desc()).all()

            if not form.validate():
                return render_template('event.html', events=result, form=form, action="detail_event")
        event_name = "Объединение чеков"
        date_from = form.start_date.data
        date_to = form.end_date.data

        events_id = \
            db.session.query(OrmEvent.id). \
                join(OrmParticipant, OrmEvent.id == OrmParticipant.c.event_id). \
                filter(and_(OrmEvent.date.between(date_from, date_to), OrmParticipant.c.person_id == current_user.id)). \
                group_by(OrmEvent.id)

        participant_id = \
            db.session.query(OrmUser.id, OrmUser.name). \
                join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                filter(OrmEvent.id.in_(events_id)). \
                group_by(OrmUser.id, OrmUser.name).\
                order_by(OrmUser.id).all()

        pay_info = \
            db.session.query(func.coalesce(func.sum(OrmPay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
                outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_id, OrmParticipant.c.person_id == OrmPay.person_id)). \
                filter(OrmEvent.id.in_(events_id)). \
                group_by(OrmParticipant.c.person_id).order_by(OrmParticipant.c.person_id).all()

        sub_debt = db.session.query(func.avg(OrmItem.cost).label("costs"), func.sum(OrmDebt.sum).label("sums"),
                                    OrmItem.id.label("id")). \
            join(OrmItem, OrmItem.id == OrmDebt.item_id). \
            join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
            join(OrmEvent, OrmEvent.id == OrmCheck.event_id). \
            filter(OrmEvent.id.in_(events_id)). \
            group_by(OrmItem.id).subquery()

        categorical_debt = \
            db.session.query(func.sum(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)),
                             OrmParticipant.c.person_id, OrmItem.category). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
                join(OrmItem, OrmItem.check_id == OrmCheck.id). \
                outerjoin(OrmDebt,
                          and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
                filter(and_(OrmEvent.id.in_(events_id), sub_debt.c.id == OrmItem.id)). \
                group_by(OrmParticipant.c.person_id, OrmItem.category). \
                order_by(OrmParticipant.c.person_id, OrmItem.category).all()

        all_debt = \
            db.session.query(func.sum(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)),
                             OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
                join(OrmItem, OrmItem.check_id == OrmCheck.id). \
                outerjoin(OrmDebt,
                          and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
                filter(and_(OrmEvent.id.in_(events_id), sub_debt.c.id == OrmItem.id)). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id).all()

        categories = \
            db.session.query(OrmItem.category). \
                join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id)). \
                join(OrmEvent, and_(OrmEvent.id == OrmCheck.event_id, OrmEvent.id.in_(events_id))). \
                group_by(OrmItem.category).order_by(OrmItem.category).all()

        who_repay = \
            db.session.query(func.coalesce(func.sum(OrmRepay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                outerjoin(OrmRepay,
                          and_(OrmRepay.id_event == OrmEvent.id, OrmRepay.id_debt == OrmParticipant.c.person_id,
                               OrmRepay.active == True)). \
                filter(OrmEvent.id.in_(events_id)). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id).all()

        whom_repay = \
            db.session.query(func.coalesce(func.sum(OrmRepay.sum), 0), OrmParticipant.c.person_id). \
                join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
                outerjoin(OrmRepay,
                          and_(OrmRepay.id_event == OrmEvent.id, OrmRepay.id_repay == OrmParticipant.c.person_id,
                               OrmRepay.active == True)). \
                filter(OrmEvent.id.in_(events_id)). \
                group_by(OrmParticipant.c.person_id). \
                order_by(OrmParticipant.c.person_id).all()

        repay = db.session.query(OrmRepay.sum, OrmRepay.id, OrmEvent.name, OrmUser.name, OrmUser.surname). \
            join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
            join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
            filter(and_(OrmRepay.id_repay == current_user.id, OrmRepay.active == False,
                        OrmEvent.id.in_(events_id))).all()

        subquery1 = db.session.query(OrmRepay.id_debt.label("debt"), OrmRepay.id_repay.label("id"),
                                     OrmRepay.sum.label("sum"), OrmUser.name.label("name1"),
                                     OrmUser.surname.label("surname1")). \
            join(OrmUser, OrmUser.id == OrmRepay.id_debt). \
            join(OrmEvent, OrmEvent.id == OrmRepay.id_event). \
            filter(and_(OrmRepay.active == True, OrmEvent.id.in_(events_id))).subquery()

        repay_all = db.session.query(subquery1.c.sum.label("sum"), OrmUser.name.label("name2"),
                                     OrmUser.surname.label("surname2"), subquery1.c.name1.label("name1"),
                                     subquery1.c.surname1.label("surname1")).join(OrmUser,
                                                                                  OrmUser.id == subquery1.c.id).order_by(
            subquery1.c.debt).all()

    if len(categories) > 0:
        return render_template('event_table.html', people=participant_id, pay=pay_info, debt=categorical_debt,
                               categories=categories, all_debts=all_debt, id=events_id, who_repay=who_repay,
                               whom_repay=whom_repay, repay=repay, repay_all=repay_all, event_name=event_name)
    else:
        return render_template('event_table_none.html')


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    form = EventForm()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()
    form.event_friends.choices = [(g.id, g.name + " " + g.surname) for g in result_request]

    if request.method == 'POST':
        if not form.validate():
            return render_template('event_form.html', form=form, form_name="New event", action="new_event",
                                   participant=None)
        else:
            new_event = OrmEvent(
                name=form.event_name.data,
                place=form.event_place.data,
                date=form.event_date.data
            )

            add_event = db.session.query(OrmUser).filter(OrmUser.id.in_(form.event_friends.raw_data)).all()
            me = db.session.query(OrmUser).filter(OrmUser.id == current_user.id).one()
            add_event.append(me)

            for i in add_event:
                i.event.append(new_event)
                db.session.add(i)

            db.session.commit()
            return redirect(url_for('events'))

    return render_template('event_form.html', form=form, form_name="New event", action="new_event", participant=None)


@app.route('/edit_event', methods=['GET', 'POST'])
@login_required
def edit_event():
    form = EventForm()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()
    form.event_friends.choices = [(g.id, g.name + " " + g.surname) for g in result_request]

    if request.method == 'GET':

        event_id = request.args.get('event_id')
        event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()

        form.event_id.data = event_id
        form.event_name.data = event.name
        form.event_place.data = event.place
        form.event_date.data = event.date

        participant = db.session.query(OrmParticipant.c.person_id). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
            filter(OrmEvent.id == event_id).all()

        participant = list(map(lambda x: x[0], participant))
        participant.remove(1)

        return render_template('event_form.html', form=form, form_name="Edit event", action="edit_event",
                               participant=participant)


    else:

        if not form.validate():
            return render_template('event_form.html', form=form, form_name="Edit event", action="edit_event")
        else:
            event = db.session.query(OrmEvent).filter(OrmEvent.id == form.event_id.data).one()

            event.name = form.event_name.data,
            event.place = form.event_place.data,
            event.date = form.event_date.data

            participates = db.session.query(OrmUser). \
                join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
                join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
                filter(OrmEvent.id == form.event_id.data)

            add_event = db.session.query(OrmUser).filter(OrmUser.id.in_(form.event_friends.raw_data))
            me = db.session.query(OrmUser).filter(OrmUser.id == current_user.id)

            to_del = participates.except_(add_event.union(me)).all()

            to_add = add_event.union(me).except_(participates).all()

            for i in to_del:
                i.event.remove(event)
                db.session.add(i)

            for i in to_add:
                i.event.append(event)
                db.session.add(i)

            db.session.commit()

            return redirect(url_for('events'))


@app.route('/delete_event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form['event_id']

    repay = db.session.query(OrmRepay).filter(OrmRepay.id_event == event_id).all()
    for i in repay:
        db.session.delete(i)

    debt = db.session.query(OrmDebt). \
        join(OrmItem, OrmItem.id == OrmDebt.item_id). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.event_id == event_id).all()
    for i in debt:
        db.session.delete(i)

    item = db.session.query(OrmItem). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.event_id == event_id).all()
    for i in item:
        db.session.delete(i)

    pay = db.session.query(OrmPay). \
        join(OrmCheck, OrmCheck.id == OrmPay.check_id). \
        filter(OrmCheck.event_id == event_id).all()
    for i in pay:
        db.session.delete(i)

    check = db.session.query(OrmCheck). \
        filter(OrmCheck.event_id == event_id).all()
    for i in check:
        db.session.delete(i)

    event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()
    db.session.delete(event)

    db.session.commit()

    return redirect(url_for('events'))


@app.route('/checks', methods=['GET'])
@login_required
def checks():
    result = db.session.query(OrmCheck.id, OrmCheck.description, OrmCheck.sum, OrmEvent.name, OrmEvent.date). \
        join(OrmEvent, OrmEvent.id == OrmCheck.event_id). \
        join(OrmParticipant, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmUser, OrmParticipant.c.person_id == OrmUser.id).filter(OrmUser.id == current_user.id). \
        order_by(OrmEvent.date.desc(), OrmCheck.id.desc()).all()

    return render_template('check.html', checks=result)


@app.route('/new_check', methods=['GET', 'POST'])
def new_check():
    form = CheckForm()
    if request.method == 'GET':
        form.check_sum.append_entry(None)
        form.check_item.append_entry(None)
        form.item_cost.append_entry(None)
        form.item_type.append_entry(None)
        form.check_pay.append_entry(None)
        form.item_id.append_entry(None)

    event_id = request.args.get('event_id')
    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id).filter(OrmEvent.id == event_id). \
        order_by(OrmUser.id).all()
    for i in range(len(form.check_pay)):
        form.check_pay[i].choices = [(g.id, g.name + " " + g.surname) for g in people]

    if request.method == 'POST':
        if not form.validate():
            return render_template('check_form.html', form=form, form_name="New check", action="new_check", id=event_id)
        else:
            add = []

            new_check = OrmCheck(
                sum=round(sum(form.check_sum.data), 2),
                description=form.check_description.data
            )

            event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()
            event.check.append(new_check)
            add.append(event)

            sale = form.check_sale.data / len(people)

            for i in range(len(form.check_pay.data)):
                new_check.user_pay.append(
                    OrmPay(person_id=form.check_pay.data[i], sum=round(form.check_sum.data[i], 2)))

            for i in range(len(form.check_item.data)):
                new_check.item.append(OrmItem(
                    name=form.check_item.data[i],
                    cost=round(form.item_cost.data[i] + sale, 2),
                    category=form.item_type.data[i]
                ))

            db.session.add(event)
            db.session.commit()

            return redirect(url_for('new_debt', id=new_check.id))

    return render_template('check_form.html', form=form, form_name="New check", action="new_check", id=event_id)


@app.route('/new_debt/<id>', methods=['GET', 'POST'])
def new_debt(id):
    form = DebtForm()

    items = db.session.query(OrmItem.id, OrmItem.name, OrmItem.cost).join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.id == id).order_by(OrmItem.id).all()

    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
        filter(OrmCheck.id == id).order_by(OrmUser.id).all()

    flag = False
    form.debt_errors = []
    if request.method == 'POST':
        for i in range(len(items)):
            if sum(list(map(lambda x: x.data,
                            form.debt_count[len(people) * i:len(people) * i + len(people)]))) == 0 and str(
                i) not in str(form.debt_all):
                form.debt_errors.append("ошибка ввода")
                flag = True
            else:
                form.debt_errors.append(None)

        if flag:
            for i in range(len(items)):
                for j in range(len(people)):
                    form.debt_count.append_entry()
                form.debt_all.append_entry()
                form.item_id.append_entry()
            return render_template('debt_form.html', form=form, form_name="New debt", action="new_debt",
                                   people=people, items=items, id=id)
        else:
            for i in range(len(items)):
                if '"debt_all-' + str(i) + '"' in str(form.debt_all):
                    price = items[i].cost / len(people)
                    for j in people:
                        deb = OrmDebt(
                            item_id=items[i].id,
                            person_id=j.id,
                            # sum=round(price, 2)
                            sum=1
                        )
                        db.session.add(deb)
                        db.session.commit()
                else:
                    count = form.debt_count.data[len(people) * i:len(people) * i + len(people)]
                    for j in range(len(people)):
                        if count[j] > 0:
                            deb = OrmDebt(
                                item_id=items[i].id,
                                person_id=people[j].id,
                                # sum=round(items[i].cost / sum(count) * count[j], 2)
                                sum=count[j]
                            )
                            db.session.add(deb)
                            db.session.commit()

        return redirect(url_for('detail_check', check_id=id))

    for i in range(len(items)):
        for j in range(len(people)):
            form.debt_count.append_entry()
        form.debt_all.append_entry()
    return render_template('debt_form.html', form=form, form_name="New debt", action="new_debt", people=people,
                           items=items, id=id)


@app.route('/detail_check', methods=['GET', 'POST'])
@login_required
def detail_check():
    check_id = request.args.get('check_id')

    names = db.session.query(OrmEvent.name, OrmCheck.description). \
        join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
        filter(OrmCheck.id == check_id).one()

    items = db.session.query(OrmItem). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.id == check_id).order_by(OrmItem.id).all()

    sub_debt = db.session.query(func.avg(OrmItem.cost).label("costs"), func.sum(OrmDebt.sum).label("sums"),
                                OrmItem.id.label("id")). \
        join(OrmItem, OrmItem.id == OrmDebt.item_id). \
        filter(OrmItem.check_id == check_id). \
        group_by(OrmItem.id).subquery()

    debt = db.session.query(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0), sub_debt.c.id,
                            OrmParticipant.c.person_id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
        join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
        join(OrmItem, OrmItem.check_id == OrmCheck.id). \
        outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
        filter(and_(OrmItem.check_id == check_id, sub_debt.c.id == OrmItem.id)). \
        order_by(sub_debt.c.id, OrmParticipant.c.person_id).all()

    debt_totals = db.session.query(func.sum(sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)),
                        OrmParticipant.c.person_id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
        join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
        join(OrmItem, OrmItem.check_id == OrmCheck.id). \
        outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
        filter(and_(OrmItem.check_id == check_id, sub_debt.c.id == OrmItem.id)). \
        group_by(OrmParticipant.c.person_id).\
        order_by(OrmParticipant.c.person_id).all()

    people = db.session.query(OrmUser). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
        filter(OrmCheck.id == check_id).order_by(OrmUser.id).all()

    pay = db.session.query(OrmPay.sum, OrmUser.name, OrmUser.surname). \
        join(OrmUser, OrmUser.id == OrmPay.person_id). \
        filter(OrmPay.check_id == check_id).all()

    return render_template('check_table.html', items=items, debt=debt, people=people, pay=pay, names=names,
                           totals=debt_totals)


@app.route('/new_repay', methods=['GET', 'POST'])
def new_repay():
    form = RepayForm()

    event_id = request.args.get('event_id')
    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id).filter(OrmEvent.id == event_id)
    me = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        filter(OrmUser.id == current_user.id)
    people = people.except_(me).order_by(OrmUser.id).all()

    form.repay_id.choices = [(g.id, g.name + " " + g.surname) for g in people]

    form.event_id.data = event_id
    form.my_id.data = current_user.id

    if request.method == 'POST':
        if not form.validate():
            return render_template('repey_form.html', form=form, form_name="New repay", action="new_repay", id=event_id)
        else:
            new_repay = OrmRepay(
                id_event=form.event_id.data,
                id_debt=form.my_id.data,
                id_repay=form.repay_id.data,
                sum=form.repay_sum.data,
                active=False
            )

            db.session.add(new_repay)
            db.session.commit()

            return redirect(url_for('detail_event', event_id=event_id))

    return render_template('repey_form.html', form=form, form_name="New repay", action="new_repay", id=event_id)


@app.route('/except_repay', methods=['POST'])
@login_required
def except_repay():
    repay_id = request.form['repay_id']

    repay = db.session.query(OrmRepay).filter(OrmRepay.id == repay_id).one()

    repay.active = True

    db.session.add(repay)
    db.session.commit()

    return {"repay_id": repay_id, "href": "detail_event?event_id=" + str(repay.id_event)}


@app.route('/deny_repay', methods=['POST'])
@login_required
def deny_repay():
    repay_id = request.form['repay_id']

    repay = db.session.query(OrmRepay).filter(OrmRepay.id == repay_id).one()

    db.session.delete(repay)
    db.session.commit()

    return jsonify(repay_id=repay_id, href="detail_event?event_id=" + str(repay.id_event))


@app.route('/detail_item', methods=['GET', 'POST'])
@login_required
def detail_item():
    event_id = request.args.get('event_id')
    category = request.args.get('category')
    person_id = request.args.get('person_id')

    sub_debt = db.session.query(func.avg(OrmItem.cost).label("costs"), func.sum(OrmDebt.sum).label("sums"),
                                OrmItem.id.label("id")). \
        join(OrmItem, OrmItem.id == OrmDebt.item_id). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.event_id == event_id). \
        group_by(OrmItem.id).subquery()

    query = \
        db.session.query(OrmCheck.description, OrmItem.name, OrmItem.category,
                         (sub_debt.c.costs / sub_debt.c.sums * func.coalesce(OrmDebt.sum, 0)).label("sum"),
                         OrmUser.name.label("pname"), OrmUser.surname). \
            join(OrmDebt, OrmDebt.item_id == OrmItem.id). \
            join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
            join(OrmEvent, OrmEvent.id == OrmCheck.event_id). \
            join(OrmParticipant, and_(OrmParticipant.c.event_id == OrmEvent.id,
                                      OrmParticipant.c.person_id == OrmDebt.person_id)). \
            join(OrmUser, OrmParticipant.c.person_id == OrmUser.id)

    if category and person_id:
        details = query.filter(and_(OrmItem.category == category, OrmCheck.event_id == event_id,
                                    OrmDebt.person_id == person_id, sub_debt.c.id == OrmItem.id)).all()
        flag = None
    elif category:
        details = query.filter(
            and_(OrmItem.category == category, OrmCheck.event_id == event_id, sub_debt.c.id == OrmItem.id)).all()
        flag = "category"
    elif person_id:
        details = query.filter(
            and_(OrmCheck.event_id == event_id, OrmDebt.person_id == person_id, sub_debt.c.id == OrmItem.id)).all()
        flag = "person"

    return render_template('item_table.html', details=details, event_id=event_id, flag=flag)


@app.route('/edit_check', methods=['GET', 'POST'])
@login_required
def edit_check():
    form = CheckForm()

    if request.method == 'GET':
        check_id = request.args.get('check_id')
        check = db.session.query(OrmCheck).filter(OrmCheck.id == check_id).one()

        people_pay = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname, OrmPay.sum). \
            join(OrmPay, OrmPay.person_id == OrmUser.id). \
            filter(OrmPay.check_id == check_id).order_by(OrmUser.id).all()

        items = db.session.query(OrmItem).filter(OrmItem.check_id == check_id).order_by(OrmItem.id).all()

        people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
            join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
            join(OrmCheck, OrmCheck.event_id == OrmEvent.id).filter(OrmCheck.id == check_id). \
            order_by(OrmUser.id).order_by(OrmUser.id).all()

        for i in items:
            form.check_item.append_entry(i.name)
            form.item_cost.append_entry(i.cost)
            form.item_type.append_entry(i.category)
            form.item_id.append_entry(i.id)
        for i in range(len(people_pay)):
            form.check_pay.append_entry(people_pay[i].id)
            form.check_pay[i].choices = [(g.id, g.name + " " + g.surname) for g in people]
            form.check_sum.append_entry(people_pay[i].sum)
        form.check_id.data = check_id
        form.check_description.data = check.description
        form.check_sale.data = 0

        return render_template('check_form.html', form=form, form_name="Edit check", action="edit_check")
    else:
        people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
            join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
            join(OrmCheck, OrmCheck.event_id == OrmEvent.id).filter(OrmCheck.id == form.check_id.data). \
            order_by(OrmUser.id).all()

        for i in range(len(form.check_pay.data)):
            form.check_pay[i].choices = [(g.id, g.name + " " + g.surname) for g in people]

        if not form.validate():
            return render_template('check_form.html', form=form, form_name="Edit check", action="edit_check")
        else:
            checks = db.session.query(OrmCheck).filter(OrmCheck.id == form.check_id.data).one()

            checks.sum = round(sum(form.check_sum.data), 2),
            checks.description = form.check_description.data

            pay = db.session.query(OrmPay).filter(OrmPay.check_id == form.check_id.data).all()

            items = db.session.query(OrmItem).filter(OrmItem.check_id == form.check_id.data).all()

            for i in range(len(form.item_id.data)):
                if form.item_id.data[i] == "":
                    sale = form.check_sale.data / len(people)
                    checks.item.append(OrmItem(
                        name=form.check_item.data[i],
                        cost=round(form.item_cost.data[i] + sale, 2),
                        category=form.item_type.data[i]
                    ))
                else:
                    item = db.session.query(OrmItem).filter(OrmItem.id == form.item_id.data[i]).one()
                    item.name = form.check_item.data[i],
                    item.cost = form.item_cost.data[i],
                    item.category = form.item_type.data[i]
            for i in items:
                if str(i.id) not in form.item_id.data:
                    debts = db.session.query(OrmDebt).filter(OrmDebt.item_id == i.id).all()
                    for j in debts:
                        db.session.delete(j)
                    db.session.delete(i)

            for i in range(len(form.check_pay.data)):
                if i < len(pay):
                    pay_u = db.session.query(OrmPay).filter(
                        and_(OrmPay.check_id == pay[i].check_id, OrmPay.person_id == pay[i].person_id)).one()
                    pay_u.sum = form.check_sum.data[i]
                    # pay_u.person_id = form.check_pay.data[i]
                    db.session.add(pay_u)
                else:
                    checks.user_pay.append(OrmPay(
                        person_id=form.check_pay.data[i],
                        sum=round(form.check_sum.data[i], 2)))
            for i in pay:
                if i.person_id not in form.check_pay.data:
                    db.session.delete(i)

            db.session.commit()

            return redirect(url_for('edit_debt', id=checks.id))


@app.route('/edit_debt/<id>', methods=['GET', 'POST'])
@login_required
def edit_debt(id):
    form = DebtForm()

    all_debt = db.session.query(func.coalesce(OrmDebt.sum, 0), OrmUser.id). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
        join(OrmCheck, OrmCheck.event_id == OrmEvent.id). \
        join(OrmItem, OrmItem.check_id == OrmCheck.id). \
        outerjoin(OrmDebt, and_(OrmDebt.item_id == OrmItem.id, OrmDebt.person_id == OrmParticipant.c.person_id)). \
        filter(OrmCheck.id == id). \
        order_by(OrmItem.id, OrmUser.id).all()

    items = db.session.query(OrmItem.id, OrmItem.name, OrmItem.cost). \
        join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.id == id).order_by(OrmItem.id).all()

    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_id == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
        filter(OrmCheck.id == id).order_by(OrmUser.id).all()

    form.debt_errors = []
    if request.method == 'GET':
        for i in range(len(items)):
            if len(list(filter(lambda x: x[0] != 0, all_debt[i * len(people):i * len(people) + len(people)]))) != len(
                    people):
                for j in range(len(people)):
                    if all_debt[i * len(people) + j][0] == 0:
                        form.debt_count.append_entry(0)
                    else:
                        form.debt_count.append_entry(int(all_debt[i * len(people) + j][0]))

                form.debt_all.append_entry()
                form.item_id.append_entry(items[i].id)
            else:
                for j in range(len(people)):
                    form.debt_count.append_entry(0)
                form.debt_all.append_entry(True)
                form.item_id.append_entry(items[i].id)

        return render_template('debt_form.html', form=form, form_name="Edit debt", action="edit_debt",
                               people=people, items=items, id=id)
    else:
        flag = False
        form.debt_errors = []
        for i in range(len(items)):
            if sum(list(map(lambda x: x.data,
                            form.debt_count[
                            len(people) * i:len(people) * i + len(people)]))) == 0 and '"debt_all-' + str(i) + '"' \
                    not in str(form.debt_all):
                form.debt_errors.append("ошибка ввода")
                flag = True
            else:
                form.debt_errors.append(None)
        if flag:
            for i in range(len(items)):
                if len(list(
                        filter(lambda x: x[0] != 0, all_debt[i * len(people):i * len(people) + len(people)]))) != len(
                    people):
                    for j in range(len(people)):
                        if all_debt[i * len(people) + j][0] == 0:
                            form.debt_count.append_entry(0)
                        else:
                            form.debt_count.append_entry(int(all_debt[i * len(people) + j][0]))

                    form.debt_all.append_entry()
                else:
                    for j in range(len(people)):
                        form.debt_count.append_entry(0)
                    form.debt_all.append_entry(True)

            return render_template('debt_form.html', form=form, form_name="Edit debt", action="edit_debt",
                                   people=people, items=items, id=id)
        else:
            for i in range(len(items)):
                if '"debt_all-' + str(i) + '"' in str(form.debt_all):
                    for j in range(len(people)):
                        deb = db.session.query(OrmDebt).filter(
                            and_(OrmDebt.item_id == items[i].id, OrmDebt.person_id == people[j].id)).one_or_none()
                        if deb == None:
                            new_deb = OrmDebt(
                                item_id=items[i].id,
                                person_id=people[j].id,
                                sum=1
                            )
                            db.session.add(new_deb)
                        else:
                            deb.sum = 1
                else:
                    count = form.debt_count.data[len(people) * i:len(people) * i + len(people)]
                    for j in range(len(people)):
                        deb = db.session.query(OrmDebt).filter(
                            and_(OrmDebt.item_id == items[i].id, OrmDebt.person_id == people[j].id)).one_or_none()
                        if form.debt_count[i * len(people) + j].data > 0 and deb != None:
                            deb.sum = count[j]
                        elif form.debt_count[i * len(people) + j].data > 0 and deb == None:
                            new_deb = OrmDebt(
                                item_id=items[i].id,
                                person_id=people[j].id,
                                sum=count[j]
                            )
                            db.session.add(new_deb)
                        elif form.debt_count[i * len(people) + j].data == 0 and deb != None:
                            db.session.delete(deb)

            db.session.commit()
        return redirect(url_for('detail_check', check_id=id))


@app.route('/delete_check', methods=['POST'])
@login_required
def delete_check():
    check_id = request.form['check_id']

    pay = db.session.query(OrmPay). \
        filter(OrmPay.check_id == check_id).all()
    for i in pay:
        db.session.delete(i)

    debt = db.session.query(OrmDebt). \
        join(OrmItem, OrmItem.id == OrmDebt.item_id). \
        filter(OrmItem.check_id == check_id).all()
    for i in debt:
        db.session.delete(i)

    item = db.session.query(OrmItem). \
        filter(OrmItem.check_id == check_id).all()
    for i in item:
        db.session.delete(i)

    check = db.session.query(OrmCheck).filter(OrmCheck.id == check_id).one()
    db.session.delete(check)

    db.session.commit()

    return redirect(url_for('checks'))


if __name__ == "__main__":
    app.debug = True
    app.run()
