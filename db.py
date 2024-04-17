'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=True)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)

# insert a new friend request
def insert_friendrequest(username: str, friendname:str):
    with Session(engine) as session:
        friendrequest = FriendRequest(username=username,friendname=friendname,status = "Pending")
        session.add(friendrequest)
        session.commit() 

# get friend request
def get_friendrequest(username:str):
    with Session(engine) as session:
      results = session.query(FriendRequest).filter(FriendRequest.username == username)
    return results

# get received friend request
def get_received_friendrequest(username:str):
    with Session(engine) as session:
      results = session.query(FriendRequest).filter(FriendRequest.friendname == username)
    return results

# modify request status
def modify_status_request(username:str, friendname:str, new_status: str):
    with Session(engine) as session:
       requests = session.query(FriendRequest).all()
    # match the corresponding row
       for r in requests:
          if(r.username == friendname and r.friendname == username):
            r.status = new_status
       session.commit()
       




# insert a new friendship
def insert_friendship(username: str, friendname:str):
    with Session(engine) as session:
        friendship = Friendship(username=username,friendname=friendname)
        session.add(friendship)
        session.commit()

# gets a user friendship
def get_friendship_sent_from_you(username:str):
    with Session(engine) as session:
      result = session.query(Friendship).filter(Friendship.username == username)
    return result

def get_friendship_received_by_you(username):
    with Session(engine) as session:
      result = session.query(Friendship).filter(Friendship.friendname == username)
    return result

# check friendship exists
def friendship_exist(username:str, friendname:str):
    with Session(engine) as session:
       friendship = session.query(FriendRequest).all()
    # match the corresponding row
       for f in friendship:
          if(f.username == friendname and f.friendname == username) or (f.username == username and f.friendname == friendname):
             return True 
    return False



# delete friendship
def delete_all():
    with Session(engine) as session:
       session.query(Friendship).delete()
       session.commit()
       session.query(FriendRequest).delete()
       session.commit()