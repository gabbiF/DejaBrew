import datetime
import hashlib
import os
import random
 
 
import bcrypt
from flask_sqlalchemy import SQLAlchemy
 
db = SQLAlchemy()
 
from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
 
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
 
import re
import string
 
 
 
class User(db.Model):
   """
   User model
   """
   __tablename__ = "users"
   id = db.Column(db.Integer, primary_key=True)
 
   # User information
   username = db.Column(db.String, nullable = False, unique=True)
   email = db.Column(db.String, nullable=False, unique=True)
   password_digest = db.Column(db.String, nullable=False) #authetication
  
   #Session information
   session_token = db.Column(db.String, nullable=False, unique=True)
   session_expiration = db.Column(db.DateTime, nullable=False)
   update_token = db.Column(db.String, nullable=False, unique=True)
 
   #Relationship with user
   preferences = db.relationship("Preference", cascade = "delete")
   posts = db.relationship("Post", cascade = "delete")
  
   def __init__(self, **kwargs):
       """
       Initializes a User object
       """
       self.username = kwargs.get("username")
       self.email = kwargs.get("email")
       self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
       self.renew_session()
 
   def _urlsafe_base_64(self):
       """
       Randomly generates hashed tokens (used for session/update tokens)
       """
       return hashlib.sha1(os.urandom(64)).hexdigest()
 
   def renew_session(self):
       """
       Renews the sessions, i.e.
       1. Creates a new session token
       2. Sets the expiration time of the session to be a day from now
       3. Creates a new update token
       """
       self.session_token = self._urlsafe_base_64()
       self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
       self.update_token = self._urlsafe_base_64()
 
   def verify_password(self, password):
       """
       Verifies the password of a user
       """
       return bcrypt.checkpw(password.encode("utf8"), self.password_digest)
 
   def verify_session_token(self, session_token):
       """
       Verifies the session token of a user
       """
       return session_token == self.session_token and datetime.datetime.now() < self.session_expiration
 
   def verify_update_token(self, update_token):
       """
       Verifies the update token of a user
       """
       return update_token == self.update_token
 
   def serialize(self):
       """
       Serialize the user object
       """
       return{
           "id" : self.id,
           "username" : self.username,
           "email" : self.email
       }

class Preference(db.Model):
   """
   Preference Model
   """
   __tablename__ = "preferences"
   id = db.Column(db.Integer, primary_key=True)
  
   # information about preferences
   matchme = db.Column(db.Boolean, nullable = False, unique=False) 
   city = db.Column(db.String, nullable=False, unique=False)
   age = db.Column(db.Integer, nullable = False, unique=False)
   drinkfav = db.Column(db.String, nullable = False, unique=False)
   caffeinemg = db.Column(db.Integer, nullable = False, unique=False)
   maxcalories = db.Column(db.Integer, nullable = False, unique=False)
   hotorcold = db.Column(db.Integer, nullable = False, unique=False)
   favspot = db.Column(db.String, nullable = False, unique=False)
   flavors = db.Column(db.String, nullable = False, unique=False)
   bio = db.Column(db.String, nullable = False, unique=False)
  
   #Relationship between preferences and the users
   user_id = db.Column(db.Integer, db.ForeignKey("users.id"),nullable = False)
  
   def __init__(self,user_id, **kwargs):
       """
       Initializes Assignment object
       """
       self.matchme = kwargs.get("matchme")
       self.city = kwargs.get("city")
       self.age = kwargs.get("age")
       self.drinkfav= kwargs.get("drinkfav")
       self.caffeinemg= kwargs.get("caffeinemg")
       self.maxcalories = kwargs.get("maxcalories")
       self.flavors = kwargs.get("flavors")
       self.hotorcold = kwargs.get("hotorcold")
       self.favspot = kwargs.get("favspot")
       self.bio = kwargs.get("bio")
       self.user_id = user_id
  
   def serialize(self):
       """
       Serializes Preference Object
       """
       return{
           "id": self.id,
           "matchme" : self.matchme,
           "city": self.city,
           "age" : self.age,
           "drinkfav" : self.drinkfav,
           "caffeinemg" : self.caffeinemg,
           "maxcalories" : self.maxcalories,
           "hotorcold" : self.hotorcold,
           "flavors": self.flavors,
           "favspot": self.favspot,
           "bio" : self.bio
       }
 
class Drink(db.Model):
   """
   Drink model
   """
   __tablename__ = "drinks"
   id = db.Column(db.Integer, primary_key=True)
  
   # information about drinks
   name = db.Column(db.String, nullable = False, unique = False)
   caffeinemg = db.Column(db.Integer, nullable = False, unique = False)
   calories = db.Column(db.Integer, nullable = False, unique = False)
   hotorcold = db.Column(db.String, nullable = False, unique = False) #change to Bool/1 or 0 for hot or cold
 
   def __init__(self, **kwargs):
       """
       Initializes drink model
       """
       self.name = kwargs.get("name")
       self.caffeinemg = kwargs.get("caffeinemg")
       self.calories = kwargs.get("calories")
       self.hotorcold = kwargs.get("hotorcold")
 
   def serialize(self):
       """
       Serializes a Drink and its information
       """
       return {
           "id" : self.id,
           "name" : self.name,
           "caffeinemg" : self.caffeinemg,
           "calories" : self.calories,
           "hotorcold" : self.hotorcold
       }

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-2.amazonaws.com"

class Post(db.Model):
  """
  Posts model
  """
  __tablename__ = "posts"
  id = db.Column(db.Integer, primary_key = True, autoincrement= True)
  content= db.Column(db.String, nullable = False)
  user_id= db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
  image_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable = False)
  created_at = db.Column(db.DateTime, nullable = False)
 
  def __init__(self, **kwargs):
     """
     Initializes instane of post
     """ 
     self.content = kwargs.get("content")
     self.user_id = kwargs.get("user_id")
     self.image_id = kwargs.get("image_id")
     self.created_at = datetime.datetime.now()
     
  def serialize(self):
     """
     Serializes the post object
     """ 
     user = User.query.filter_by(id=self.user_id).first()
     image = Asset.query.filter_by(id = self.image_id).first()
     return{
         "id": self.id,
         "content": self.content,
         "username": user.username,
         "image": image.serialize()
     }
 
class Asset(db.Model):
  """
  Asset model
  """
  __tablename__ = "assets"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  base_url= db.Column(db.String, nullable= True)
  salt = db.Column(db.String, nullable = False)
  extension = db.Column(db.String, nullable = False)
  width = db.Column(db.Integer, nullable = False)
  height= db.Column(db.Integer, nullable = False)
  created_at = db.Column(db.DateTime, nullable = False)
 
  post = db.relationship("Post", cascade = "delete")
  def __init__(self, **kwargs):
      """
      Initializes an Asset object
      """
      self.create(kwargs.get("image_data"))
  def serialize(self):
      """
      Serializes an Asset object
      """
      return {
          "url": f"{self.base_url}/{self.salt}.{self.extension}",
          "created_at": str(self.created_at)
      }
  def create(self, image_data):
      """
      Given an image in base64 form, does the following:
      1. Rejects the image if it is not a support filetype
      2. Generates a random string for the image filename
      3. Decodes the image and attempts to upload it to AWS
      """
      try:
          ext = guess_extension(guess_type(image_data)[0])[1:]
          #only accept suported file extensions
          if ext not in EXTENSIONS:
              raise Exception(f"Unsupported file type: {ext}")
          #secure way of generating a random string for image filename
          salt = "".join(
              random.SystemRandom().choice(
                  string.ascii_uppercase + string.digits
              )
              for _ in range(16)
          )
          #remove header of base64string
          img_str = re.sub("^data:image/.+;base64,", "", image_data)
          img_data = base64.b64decode(img_str)
          img = Image.open(BytesIO(img_data))
          self.base_url = S3_BASE_URL
          self.salt = salt
          self.extension = ext
          self.width = img.width
          self.height = img.height
          self.created_at = datetime.datetime.now()
          img_filename = f"{self.salt}.{self.ext}"
          self.upload(img, img_filename)
      except Exception as e:
          print(f"Error when creating image: {e}")
        
  def upload(self, img, img_filename):
      """
      Attempts to upload the image to the specified S3 bucket
      """
      try:
          #save the image temporarily on server
          image_temploc = f"{BASE_DIR}/{img_filename}"
          img.save(image_temploc)
        
          #upload image to s3
          s3_client = boto3.client("s3")
          s3_client.upload_file(image_temploc, S3_BUCKET_NAME, img_filename)
          #make s3 image url public
          s3_resource = boto3.resource("s3")
          object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
          object_acl.put(ACL ="public-read")
          #remove image from server
          os.remove(image_temploc)

      except Exception as e:
          print(f"Error when uploading image: {e}")
