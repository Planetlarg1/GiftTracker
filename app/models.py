from app import db
from flask_login import UserMixin

# M-M Relationship users-wishlists
user_wishlist = db.Table(
    'user_wishlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),           # Foreign Key for user
    db.Column('wishlist_id', db.Integer, db.ForeignKey('wishlist.id'), primary_key=True)    # Foreign Key for Wishlist
)

# USER
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)                                            # Primary key
    username = db.Column(db.String(40), unique=True, nullable=False)                        # Unique username
    password = db.Column(db.String(128), nullable=False)                                    # Password
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)            # Foreign key for user's family
    wishlists = db.relationship(                                                            # Relation to wishlists (M-M for shared wishlists)
        'WishList', 
        secondary=user_wishlist, 
        back_populates='collaborators')                     

# FAMILY
class Family(db.Model):
    __tablename__ = 'family'
    id = db.Column(db.Integer, primary_key=True)                                            # Primary key
    name = db.Column(db.String(40), nullable=False)                                         # Family name
    join_code = db.Column(db.String(8), unique=True, nullable=False)                        # Unique family join code
    users = db.relationship('User', backref='family', lazy=True)                            # Relation to users

# WISHLIST
class WishList(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)                                            # Primary key
    name = db.Column(db.String(100), nullable=False)                                         # Wishlist name
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)           # Foriegn key for family
    collaborators = db.relationship(                                                        # Relation to Users (M-M for shared wishlists)
        'User',
        secondary=user_wishlist,
        back_populates='wishlists'
    )
    gifts = db.relationship('Gift', backref='wishlist', cascade='all, delete', lazy=True)   # Relation to gifts - delete gifts on wishlist deletion

# GIFT
class Gift(db.Model):
    __tablename__ = 'gift'
    id = db.Column(db.Integer, primary_key=True)                                            # Primary key
    name = db.Column(db.String(100), nullable=False)                                        # Gift name
    price = db.Column(db.Float, nullable=False)                                              # Gift price    
    link = db.Column(db.String(200), nullable=True)                                         # Link to gift site
    description = db.Column(db.Text, nullable=True)                                         # Gift description
    priority = db.Column(db.Integer, nullable=False)                                        # Gift priority scaling
    bought = db.Column(db.Boolean, default=False)                                           # Bough/Unbought
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlist.id'), nullable=False)       # Foreign key for wishlist