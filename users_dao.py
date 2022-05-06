"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""
from db import db
from db import User
from db import Preference
from db import Drink

#Starting user methods
def get_user_by_email(email):
    """
    Returns a user object from the database given an email
    """
    return User.query.filter(User.email == email).first()

def get_user_by_id(id): 
    """
    Returns user object from the database given the id
    """
    return User.query.filter(User.id == id).first()

def get_preference_by_user_id(user_id): 
    """
    Returns a user's preferences by the id
    """
    return Preference.query.filter(Preference.user_id == user_id).first()

#Starting preference and drink methods

def create_preference(matchme, age, city, caffeinemg, maxcalories, drinkfav, favspot, flavors, hotorcold, bio, user_id): 
    """
    Creates an instance of the preference model
    """
    optional_preference = get_preference_by_user_id(user_id)

    if optional_preference is not None: 
        return False, optional_preference
    preference = Preference(user_id = user_id, matchme = matchme, age = age, city = city, caffeinemg= caffeinemg, maxcalories = maxcalories, drinkfav = drinkfav, favspot = favspot, flavors = flavors, hotorcold = hotorcold, bio = bio)
    db.session.add(preference)
    db.session.commit()
    return True, preference

def create_drink(name, caffeinemg, calories, hotorcold):
    """
    Creates an instance of the Drink model. DOES NOT COMMIT
    """
    drink = Drink(name = name, caffeinemg = caffeinemg, calories = calories, hotorcold = hotorcold)
    db.session.add(drink)

def get_all_drinks():
    dlist = []
    drinks = Drink.query.all()
    for drink in drinks:
        dlist.append(drink.serialize())
    
    return dlist

#Authentication methods

def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    return User.query.filter(User.update_token == update_token).first()

#Methods made to support front end

def get_user_by_username(username): 
    """
    Returns a user object from the database given an its username
    """
    return User.query.filter(User.username == username).first()

#More authentication

def verify_credentials(username, password):
    """
    Returns true if the credentials match, otherwise returns false
    """
    optional_user = get_user_by_username(username)

    if optional_user is None: 
        return False, None
    return optional_user.verify_password(password), optional_user

#Creating User and renewing session methods

def create_user(username,email, password):
    """
    Creates a User object in the database

    Returns if creation was successful, and the User object
    """
    optional_user = get_user_by_email(email)

    if optional_user is not None: 
        return False, optional_user
    user = User(username = username, email = email, password= password)
    db.session.add(user)
    db.session.commit()
    return True, user

def renew_session(update_token):
    """
    Renews a user's session token
    
    Returns the User object
    """
    user = get_user_by_update_token(update_token)
    if user is None: 
        raise Exception("Invalid update token")
    user.renew_session(); 
    db.session.commit()
    return user



