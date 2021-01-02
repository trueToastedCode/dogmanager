from models import *
from app import DBASE_FILE_NAME
import os
# from shutil import copyfile

if __name__ == '__main__':
    person_names = ["Eveline", "Rolf", "Lennard", "Lukas", "Niklas", "Hildegard", "Lilly", "Leyla"]
    dog_names = ['Bonita']

    if os.path.exists(DBASE_FILE_NAME):
        # create backup
        # copyfile(DBASE_FILE_NAME, f'{get_date(p_format="%Y-%m-%d_%H-%M-%S")}-{DBASE_FILE_NAME}')
        # delete current
        mds = [Dog, Feeding, Person, Walk]
        fail_counter = 0
        for md in mds:
            try:
                db.session.query(md).delete()
            except:
                fail_counter += 1
                print('[FAIL] ' + md.__class__.__name__)
        if fail_counter != 0:
            print(f'({fail_counter} failures)')
    else:
        db.create_all()

    for person_name in person_names:
        person = Person(name=person_name)
        db.session.add(person)

    for dog_name in dog_names:
        dog = Dog(name=dog_name)
        db.session.add(dog)

    db.session.commit()
