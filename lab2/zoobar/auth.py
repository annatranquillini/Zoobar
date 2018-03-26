from zoodb import *
from debug import *

import hashlib
import random
import os
import pbkdf2
import bank_client

def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput).hexdigest()
    db.commit()
    return cred.token

def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None
    if cred.password == pbkdf2.PBKDF2(password, cred.salt).hexread(32):
        return newtoken(db, cred)
    else:
        return None

def register(username, password):
    db = person_setup()
    db1 = cred_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newcred = Cred()
    newcred.username = username
    newcred.salt = os.urandom(8).encode('base_64')
    newcred.password = pbkdf2.PBKDF2(password, newcred.salt).hexread(32)
    newperson.username = username
    db.add(newperson)
    db1.add(newcred)
    db1.commit()
    db.commit()
    bank_client.register(username)
    return newtoken(db1, newcred)

def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False

