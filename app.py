import json
 
from db import db
from db import Drink, Preference, User, Post, Asset
from flask import Flask, request
import users_dao
import datetime
import random
import time
import atexit
 
import os
from sqlalchemy import desc
 
db_filename = "auth.db"
app = Flask(__name__)
 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialization of static information within Drink model
@app.before_first_request
def before_first_request_func():
    """
    Initializes drinks table in Drink model
    """
    users_dao.create_drink("Brewed Coffee - Dark Roast", 5, 340, "Hot")
    users_dao.create_drink("Brewed Coffee - Decaf Pike Place", 5, 30, "Hot")
    users_dao.create_drink("Brewed Coffee - Medium Roast", 5, 360, "Hot")
    users_dao.create_drink("Caffe Misto", 130, 150, "Hot")
    users_dao.create_drink("Iced Coffee", 3, 200, "Cold")
    users_dao.create_drink("Cold Brewed Coffee", 3, 200, "Cold")
    users_dao.create_drink("Vanilla Sweet Cream Cold Brew", 110, 185, "Cold")
    users_dao.create_drink("Caffe Latte", 230, 150, "Hot")
    users_dao.create_drink("Iced Caffe Latte", 150, 150, "Cold")
    users_dao.create_drink("Caffe Mocha", 400, 175, "Hot")
    users_dao.create_drink("Iced Caffe Mocha", 360, 175, "Cold")
    users_dao.create_drink("Cappucino", 140, 150, "Hot")
    users_dao.create_drink("Caramel Macchiato", 280, 150, "Cold")
    users_dao.create_drink("Cinnamon Dolce Latte", 5, 340, "Hot")
    users_dao.create_drink("Flat White", 220, 195, "Hot")
    users_dao.create_drink("Skinny Mocha", 160, 150, "Hot")
    users_dao.create_drink("Iced Skinny Mocha", 120, 150, "Cold")
    users_dao.create_drink("Doubleshot on Ice", 110, 225, "Cold")
    users_dao.create_drink("White Chocolate Mocha", 500, 150, "Hot")
    users_dao.create_drink("Iced White Chocolate Mocha", 470, 150, "Cold")
    users_dao.create_drink("Chai Latte", 270, 95, "Hot")
    users_dao.create_drink("Iced Chai Latte", 260, 95, "Cold")
    users_dao.create_drink("Green Tea Latte", 280, 80, "Hot")
    users_dao.create_drink("Iced Green Tea Latte", 250, 80, "Cold")
    db.session.commit()

db.init_app(app)
with app.app_context():
   db.create_all()

   drinks = Drink.query.all()
   if len(drinks) == 0:
       before_first_request_func()
  
# generalized response formats
def success_response(data, code=200):
   """
   Generalized success response function
   """
   return json.dumps(data), code
 
def failure_response(message, code=400):
   """
   Generalized failure response function
   """
   return json.dumps({"error": message}), code
 
#TOKEN ROUTES
  
def extract_token(request):
   """
   Helper function that extracts the token from the header of a request
   """
   auth_header = request.headers.get("Authorization")
 
   if auth_header is None:
       return False, json.dumps({"Missing authorization header"}) #helper function return tuple
 
   bearer_token = auth_header.replace("Bearer", "").strip()
 
   return True, bearer_token
 
#USER FUNCTIONS
 
@app.route("/register/", methods=["POST"])
def register_account():
   """
   Endpoint for registering a new user
   """
   body = json.loads(request.data)
   username = body.get("username")
   email = body.get("email")
   password = body.get("password")
  
   if email is None or password is None:
       return failure_response("Missing email or password")
 
   was_successful, user = users_dao.create_user(username,email,password)
  
   if not was_successful:
       return failure_response("User already exists")
   return success_response(
       {
           "id" : user.id,
           "session_token" : user.session_token,
           "session_expiration": str(user.session_expiration),
           "update_token" : user.update_token
       }, 201
   )
 
@app.route("/user/<int:user_id>/")
def get_user_by_id(user_id):
   """
   Endpoint for getting a user by id
   """
   user = users_dao.get_user_by_id(user_id)
   if user is None:
       return failure_response("Could not find user at this id")
   return success_response(user.serialize())
 
@app.route("/userP/<int:user_id>/")
def get_userP(user_id):
    """
    Endpoint for getting a user and their preferences.
    """
    user = users_dao.get_user_by_id(user_id)
    if user is None:
       return failure_response("Could not find user at this id")
    preference = users_dao.get_preference_by_user_id(user_id)
    if preference is None:
       return failure_response("User has no preferences")
    userP = {**user.serialize(), **preference.serialize()}
    return success_response(userP)
 
@app.route("/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
  """
  Endpoint for deleting a user by id
  """
  user = User.query.filter_by(id= user_id).first()
  if user is None:
      return failure_response("User not found")
  db.session.delete(user)
  db.session.commit()
  return success_response(user.serialize())
   
#PREFERENCE FUNCTIONS

@app.route("/preferences/<int:user_id>/", methods= ["POST"])
def make_preferences(user_id):
   """
   Endpoint for initalizing the user preferences
   """
   get_user_by_id(user_id)
   body = json.loads(request.data)
   matchme= body.get("matchme")
   city = body.get("city")
   age = body.get("age")
   caffeinemg = body.get("caffeinemg")
   maxcalories = body.get("maxcalories")
   hotorcold = body.get("hotorcold")
   drinkfav = body.get("drinkfav")
   favspot = body.get("favspot")
   flavors = body.get("flavors")
   bio = body.get("bio")
   if city is None or age is None or caffeinemg is None or maxcalories is None or hotorcold is None or matchme is None:
       return failure_response("Mising information")
   if drinkfav is None or favspot is None or bio is None:
       return failure_response("Missing information")
  
   was_successful, preference = users_dao.create_preference(matchme, age, city , caffeinemg, maxcalories, drinkfav, favspot, flavors, hotorcold, bio, user_id)
   if not was_successful:
       return failure_response("User already has preferences")
   return success_response(preference.serialize(), 201)
 
@app.route("/preferences/<int:user_id>/update/", methods = ['POST'])
def update_preferences(user_id):
   """
   Endpoint to update user preferences.
   """
   user = users_dao.get_user_by_id(user_id)
   if user is None:
       return failure_response("Invalid User", 404)
   preference = Preference.query.filter_by(user_id = user_id).first()
   body = json.loads(request.data)
   matchme= body.get("matchme")
   city = body.get("city")
   age = body.get("age")
   caffeinemg = body.get("caffeinemg")
   maxcalories = body.get("maxcalories")
   hotorcold = body.get("hotorcold")
   drinkfav = body.get("drinkfav")
   favspot = body.get("favspot")
   flavors = body.get("flavors")
   bio = body.get("bio")
   if city is None or age is None or caffeinemg is None or maxcalories is None or hotorcold is None or matchme is None:
       return failure_response("Missing information")
   if drinkfav is None or favspot is None or bio is None:
       return failure_response("Missing information")
 
   preference.matchme = matchme
   preference.city = city
   preference.age = age
   preference.caffeinemg = caffeinemg
   preference.maxcalories = maxcalories
   preference.hotorcold = hotorcold
   preference.drinkfav = drinkfav
   preference.favspot = favspot
   preference.flavors =flavors
   preference.bio = bio
   db.session.commit()
 
   new_pref = Preference.query.filter_by(user_id = user_id).first()
   return success_response(new_pref.serialize(), 201)
 
@app.route("/preference/<int:user_id>/")
def get_pref_by_user(user_id):
   """
   Endpoint to get preferences by user id
   """
   user = users_dao.get_user_by_id(user_id)
   if user is None:
       return failure_response("Invalid user")
   preference = users_dao.get_preference_by_user_id(user_id)
   if preference is None:
       return failure_response("This user does not have any preferences")
   return success_response(preference.serialize())
 
@app.route("/preference/match/<int:user_id>/")
def get_user_matches(user_id): 
    """
    Searches users and returns 3 random matches (user ids) with the given user:
    1 in the same city
    1 with the same favorite drink
    1 with the same favorite flavor
    """
    base_user = users_dao.get_preference_by_user_id(user_id)

    base_city = base_user.city
    base_drinkfav = base_user.drinkfav
    base_flavor = base_user.flavors

    match_city = Preference.query.filter(Preference.city == base_city, Preference.matchme == True, Preference.user_id != user_id).all()
    match_drinkfav = Preference.query.filter(Preference.drinkfav == base_drinkfav, Preference.matchme == True, Preference.user_id != user_id).all()
    match_flavor = Preference.query.filter(Preference.flavors == base_flavor, Preference.matchme == True, Preference.user_id != user_id).all()

    matchdict = {}

    cityuser = None
    drinkfavuser = None
    flavoruser = None

    if len(match_city) != 0:
        citymatch = random.choice(match_city).user_id
        cityuser = User.query.filter_by(id = citymatch).first().serialize()
        matchdict["city"] = cityuser
    
    if len(match_drinkfav) != 0:
        drinkfavmatch = random.choice(match_drinkfav).user_id
        drinkfavuser = User.query.filter_by(id = drinkfavmatch).first().serialize()
        if cityuser is not None and drinkfavmatch != citymatch:
            matchdict["favoritedrink"] = drinkfavuser
    
    if len(match_flavor) != 0:
        flavormatch = random.choice(match_flavor).user_id
        flavoruser = User.query.filter_by(id = flavormatch).first().serialize()
        if cityuser is not None and drinkfavmatch == citymatch or drinkfavuser is not None and flavormatch == drinkfavmatch:
            flavoruser == None
        else:
            matchdict["flavor"] = flavoruser

    if len(matchdict) == 0:
        return json.dumps({"error" : "No users matching your city, favorite drink, or favorite flavor were found."}), 404
    
    return json.dumps({"matches" : matchdict}), 200

# DRINK FUNCTIONS

@app.route("/drink/")
def get_all_drinks():
    """
    Endpoint for getting all drinks
    """
    dlist = []
    drinks = Drink.query.all()
    for drink in drinks:
       dlist.append(drink.serialize())
  
    return json.dumps({"drinks" : dlist}), 200
 
@app.route("/drink/<int:user_id>/")
def drinkmatch(user_id):
   """
   Returns a drink object based on user preferences
   """
   base_user = users_dao.get_preference_by_user_id(user_id)
 
   base_caffeine = base_user.caffeinemg
   base_calories = base_user.maxcalories
   base_hotorcold = base_user.hotorcold
 
   drinkmatches = Drink.query.filter(base_caffeine >= Drink.caffeinemg, base_calories >= Drink.calories, base_hotorcold == Drink.hotorcold).all()
 
   if drinkmatches is None:
       return json.dumps({"error" : "No drink matches found with your preferences."}), 404
 
   drink = random.choice(drinkmatches)
 
   return json.dumps({"randomdrinkmatch" : drink.serialize()})
  
#AUTHENTICATION
 
@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    
    if username is None or password is None:
        return failure_response("Missing username or password",400)
        
    was_successful, user = users_dao.verify_credentials(username, password)
    usera = users_dao.get_user_by_username(username =username)

    if not was_successful:
        return failure_response("Incorrect username or password", 401)
    return success_response(
        {
            "id" : usera.id,
            "session_token": user.session_token,
            "session_expiration" : str(user.session_expiration),
            "update_token": user.update_token
        }
        , 201
            )
 
@app.route("/session/", methods=["POST"])
def update_session():
   """
   Endpoint for updating a user's session
   """
   was_successful, update_token = extract_token(request)
 
   if not was_successful:
       return update_token
 
   try:
       user = users_dao.renew_session(update_token)
   except Exception as e:
       return failure_response(f"Invalid update token: {str(e)}" )
 
   return success_response({
       "session_token": user.session_token,
       "session_expiration" : str(user.session_expiration),
       "update_token": user.update_token
   } , 201)
 
@app.route("/logout/", methods = ["POST"])
def logout():
    """
    Endpoint for logging a user out
    """
    was_successful, session_token = extract_token(request)
 
    if not was_successful:
       return session_token
    user = users_dao.get_user_by_session_token(session_token)
 
    if user is None:
       return failure_response("Inavalid session token")
    user.session_expiration = datetime.datetime.now()
    db.session.commit()
 
    return success_response({
       "message" : "You have successfully logged out!"
   })
 
#POST FUNCTIONS

@app.route("/posts/<int:user_id>/", methods=["POST"])
def create_post(user_id):
   """
   Endpoint for creating a post
   """
   body = json.loads(request.data)
   content= body.get("content")
   if content is None:
       return failure_response("did not provide content", 400)
   user = User.query.filter_by(id=user_id).first()
   if user is None:
       return failure_response("User not found")

   image_data = body.get("image_data")
   if image_data is None:
      return failure_response("No base64 image to be found")
   asset = Asset(image_data = image_data)
   db.session.add(asset)
   db.session.commit()

   new_post = Post(content= content, user_id = user_id, image_id = asset.id)
   "user.posts.append(new_post)"
   db.session.add(new_post)
   db.session.commit()
 
   return success_response(new_post.serialize(), 201)
   
@app.route("/get/posts/")
def get_course():
   """
   Endpoint for getting last ten posts
   """
   posts = Post.query.order_by(desc(Post.created_at)).limit(10).all()
   return success_response({"posts": [i.serialize() for i in posts]})
 
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)