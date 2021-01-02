from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from models import *
from keys import *
import json
import datetime

"""
DOCUMENTATION

Paths:
[DOG]
dogs : GET

[PERSON]
persons : GET

[WALK]
walk : GET, Params
walk-create : POST, Content
walk-mod : PUT, Content
walk-del : DELETE, Content

[FEEDING]
feeding : GET, Params
feeding-create : POST, Content
feeding-mod : PUT, Content
feeding-del : DELETE, Content
"""

### Config ###
HOST = '0.0.0.0'
PORT = '8080'
DBASE_FILE_NAME = 'database.db'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DBASE_FILE_NAME
db = SQLAlchemy(app)
### Config ###


def parse_date(p_date: str):
    return datetime.datetime.strptime(p_date, DATE_FORMAT)


def str_date(p_date: datetime.datetime):
    return p_date.strftime(DATE_FORMAT)


# check if keys are existing and not None
def are_keys(p_dic: dict, p_keys: list):
    for key in p_keys:
        if key not in p_dic.keys() or p_dic[key] is None:
            return key
    return None


def get_response_msg(p_code: int, p_msg: str):
    return Response(p_msg, status=p_code, mimetype='text/plain')


def get_response_dic(p_code: int, p_dic: dict):
    return Response(json.dumps(p_dic), status=p_code, mimetype='application/json')

### HTTP Paths ###


@app.route('/dogs', methods=['GET'])
def dogs_get():
    db_dogs = db.session.query(Dog).all()
    dogs = []
    for db_dog in db_dogs:
        dogs.append(db_dog.get_dict())
    return get_response_dic(p_code=200, p_dic=dogs)


@app.route('/persons', methods=['GET'])
def persons_get():
    db_persons = db.session.query(Person).all()
    persons = []
    for db_person in db_persons:
        persons.append(db_person.get_dict())
    return get_response_dic(p_code=200, p_dic=persons)


# required: walk
@app.route('/walk', methods=['GET'])
def walk_get():
    walk_id = request.args.get(KEY_WALK_ID)
    if walk_id is None:
        return get_response_msg(500, f'{KEY_WALK_ID} is missing!')
    walk = db.session.query(Walk).filter_by(id=walk_id).first()
    if walk is None:
        return get_response_msg(500, f'Invalid {KEY_WALK_ID}!')
    return get_response_dic(200, walk.get_dict())


# required: dog, person
# optional: date start, date end, pause
@app.route('/walk-create', methods=['POST'])
def walk_create():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_DOG_ID, KEY_PERSON_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # dog
    dog = db.session.query(Dog).filter_by(id=cont[KEY_DOG_ID]).first()
    if dog is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DOG_ID}!')
    # person
    person = db.session.query(Person).filter_by(id=cont[KEY_PERSON_ID]).first()
    if person is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PERSON_ID}!')
    # date start
    try:
        date_start = cont[KEY_DATE_START]
        if date_start is None:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_START}!')
        try:
            date_start = parse_date(date_start)
        except ValueError:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_START}!')
    except KeyError:
        date_start = datetime.datetime.now()
    # date end
    try:
        date_end = cont[KEY_DATE_END]
        if date_end is None:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_END}!')
        try:
            date_end = parse_date(date_end)
        except ValueError:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_END}!')
    except KeyError:
        date_end = None
    # pause
    try:
        pause_in_min = cont[KEY_PAUSE_IN_MIN]
        # assert isinstance(pause_in_min, str)
        if not pause_in_min.isdigit():
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PAUSE_IN_MIN}!')
    except KeyError:
        pause_in_min = 0
    # create walk
    walk = person.walk(p_dog=dog, p_date_start=date_start, p_date_end=date_end, p_pause_in_min=pause_in_min)
    return get_response_msg(p_code=200, p_msg=str(walk.id))


# required: walk
# optional: person, date start, date end, person, pause
@app.route('/walk-mod', methods=['PUT'])
def walk_mod():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_WALK_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # get walk
    try:
        walk = db.session.query(Walk).filter_by(id=cont[KEY_WALK_ID]).first()
        if walk is None:
            raise ValueError
    except:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_WALK_ID}')
    # person
    try:
        person = db.session.query(Person).filter_by(id=cont[KEY_PERSON_ID]).first()
        if person is None:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PERSON_ID}')
        walk.person_id = cont[KEY_PERSON_ID]
    except KeyError:
        None
    # date start
    try:
        date_start = cont[KEY_DATE_START]
        try:
            date_start = parse_date(date_start)
        except ValueError:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_START}')
        walk.date_start = date_start
    except KeyError:
        None
    # date end
    try:
        date_end = cont[KEY_DATE_END]
        try:
            date_end = parse_date(date_end)
        except ValueError:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE_END}')
        walk.date_end = date_end
    except KeyError:
        None
    # pause
    try:
        pause_in_min = cont[KEY_PAUSE_IN_MIN]
        # assert isinstance(pause_in_min, str)
        if pause_in_min is None or not pause_in_min.isdigit():
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PAUSE_IN_MIN}!')
        walk.pause_in_min = pause_in_min
    except KeyError:
        None
    # save
    db.session.commit()
    return Response(status=200)


# required: walk
@app.route('/walk-del', methods=['DELETE'])
def walk_del():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_WALK_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # feeding
    walk = db.session.query(Walk).filter_by(id=cont[KEY_WALK_ID]).first()
    if walk is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_WALK_ID}')
    # delete
    db.session.delete(walk)
    db.session.commit()
    return Response(status=200)


# required: feeding
@app.route('/feeding', methods=['GET'])
def feeding_get():
    feeding_id = request.args.get(KEY_FEEDING_ID)
    if feeding_id is None:
        return get_response_msg(500, f'{KEY_FEEDING_ID} is missing!')
    feeding = db.session.query(Feeding).filter_by(id=feeding_id).first()
    if feeding is None:
        return get_response_msg(500, f'Invalid {KEY_FEEDING_ID}!')
    return get_response_dic(200, feeding.get_dict())


# required: dog, person
# optional: date
@app.route('/feeding-create', methods=['POST'])
def feeding_create():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_PERSON_ID, KEY_DOG_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # person
    person = db.session.query(Person).filter_by(id=cont[KEY_PERSON_ID]).first()
    if person is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PERSON_ID}')
    # dog
    dog = db.session.query(Dog).filter_by(id=cont[KEY_DOG_ID]).first()
    if dog is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DOG_ID}')
    # date
    try:
        date = cont[KEY_DATE]
        try:
            date = parse_date(date)
        except:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE}')
    except KeyError:
        date = datetime.datetime.now()
    # create feeding
    feeding = person.feed(p_dog=dog, p_date=date)
    return get_response_msg(p_code=200, p_msg=str(feeding.id))


# required: feeding
# optional: date, person, dog
@app.route('/feeding-mod', methods=['POST'])
def feeding_mod():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_FEEDING_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # feeding
    feeding = db.session.query(Feeding).filter_by(id=cont[KEY_FEEDING_ID]).first()
    if feeding is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_FEEDING_ID}')
    # date
    try:
        date = cont[KEY_DATE]
        try:
            date = parse_date(date)
        except:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DATE}')
        feeding.date = date
    except KeyError:
        None
    # person
    try:
        person = db.session.query(Person).filter_by(id=cont[KEY_PERSON_ID]).first()
        if person is None:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_PERSON_ID}')
        feeding.person_id = person.id
    except KeyError:
        None
    # dog
    try:
        dog = db.session.query(Dog).filter_by(id=cont[KEY_DOG_ID]).first()
        if dog is None:
            return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_DOG_ID}')
        feeding.dog_id = dog.id
    except KeyError:
        None
    # save
    db.session.commit()
    return Response(status=200)


# required: feeding
@app.route('/feeding-del', methods=['DELETE'])
def feeding_del():
    cont = request.form.to_dict(flat=True)
    # check required keys
    r = are_keys(cont, [KEY_FEEDING_ID])
    if r is not None:
        return get_response_msg(p_code=500, p_msg=f'{r} is missing!')
    # feeding
    feeding = db.session.query(Feeding).filter_by(id=cont[KEY_FEEDING_ID]).first()
    if feeding is None:
        return get_response_msg(p_code=500, p_msg=f'Invalid {KEY_FEEDING_ID}')
    # delete
    db.session.delete(feeding)
    db.session.commit()
    return Response(status=200)

### HTTP Paths ###


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
