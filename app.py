

# TODO:
# Messages on wall sorted by number of likes
# If you like your own message, you go to bottom of likes list

from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy			# instead of mysqlconnection
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func                         # ADDED THIS LINE FOR DEFAULT TIMESTAMP
from flask_migrate import Migrate			# this is new
app = Flask(__name__)
# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enhanced_wall.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# an instance of the ORM
db = SQLAlchemy(app)
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)

app.secret_key = "secretstuff"
bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, 
                         # which is made by invoking the function Bcrypt with our app as an argument



likes_table = db.Table('likes',
db.Column('user_id', db.Integer, db.ForeignKey('Users.id', ondelete='cascade'), primary_key=True),
db.Column('tweet_id', db.Integer, db.ForeignKey('Tweets.id', ondelete='cascade'), primary_key=True))


follows_table = db.Table('follows',
db.Column('user_being_followed', db.Integer, db.ForeignKey('Users.id', ondelete='cascade')))



class Users(db.Model):	
    __tablename__ = "Users"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    password = db.Column(db.String(255))
    tweet_id = db.relationship('Tweets', secondary=likes_table)
    tweets = db.relationship("Tweets", backref="Users")
    user_being_followed = db.relationship('Users', secondary=follows_table)
    user_following = db.relationship('Users', secondary=follows_table)

    # group_id = db.Column(db.ForeignKey(Group.id))
    # group = db.relationship(Group, backref='users')


    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())



class Tweets(db.Model):	
    __tablename__ = "Tweets"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    liker_id = db.relationship(Users, secondary=likes_table)
    # likes = db.relationship("likes", backref="Tweets")
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())







# routes go here...

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    # Do Validation Here
    isValid = True

    fname = request.form['first_name']
    lname = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    if len(fname) < 1:
        isValid = False
        flash('Please fill in first name')

    if len(lname) < 1:
        isValid = False
        flash('Please fill in last name')

    if len(email) < 1:
        isValid = False
        flash('Please fill in email')

    if len(password) < 6:
        isValid = False
        flash('Please fill in password, must be at least 6 characters')



    # If Valid, add to DB
    if isValid:
        new_user = Users(first_name = fname, last_name = lname, email = email, password = password)
        db.session.add(new_user)
        db.session.commit()
        
        this_user = Users.query.filter_by(email = email).all()
        session['user_id'] = this_user[0].id
        return redirect('/dashboard')
    else:
        return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():

    # DO validation here
    email = request.form['loginEmail']
    password = request.form['loginPassword']
    
    this_user = Users.query.filter_by(email = email).all()

    print('******************************************************')
    print(this_user)
    print('******************************************************')
    if this_user:
        if this_user[0].password == password:
            session['user_id'] = this_user[0].id
            return redirect('/dashboard')
        else:
            flash('Incorrect Password')
    else:
        return redirect('/')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    tweets = Tweets.query.all()
    uid = session['user_id']
    return render_template('dashboard.html', tweets = tweets, currentUserid = uid)

    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/tweets/<id>/details')
def tweet_details(id):
    currentTweet = Tweets.query.get(id)
    userList = currentTweet.liker_id
    currentUser = Users.query.get(session['user_id'])
    if currentUser in userList:
        likeTest = True
    else:
        likeTest = False

    return render_template('details.html', tweet = currentTweet, likingUsers = userList, likeTest = likeTest)

@app.route('/tweets/<id>/delete')
def tweet_delete(id):
    
    tweet_to_delete = Tweets.query.get(id)
    db.session.delete(tweet_to_delete)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/tweets/<id>/like')
def tweet_like(id):
    
    tweet_to_like = Tweets.query.get(id)
    liking_user = Users.query.get(session['user_id'])
    tweet_to_like.liker_id.append(liking_user)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/tweets/<id>/unlike')
def tweet_unlike(id):
    
    tweet_to_like = Tweets.query.get(id)
    liking_user = Users.query.get(session['user_id'])
    tweet_to_like.liker_id.remove(liking_user)
    db.session.commit()

    return redirect('/dashboard')

    
@app.route('/tweets/create', methods=['POST'])
def tweets_create():
    tweet = request.form['tweet']
    user_id = session['user_id']


    if len(tweet) > 4:
        new_tweet = Tweets(tweet=tweet, user_id = user_id)
        db.session.add(new_tweet)
        db.session.commit()
    else:
        flash('tweet must be at least 5 characters long')

    return redirect('/dashboard')
    


if __name__ == "__main__":
    app.run(debug=True)




















