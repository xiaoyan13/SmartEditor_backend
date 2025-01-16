from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..article_config.models import ArticleConfig

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    
    article_configs: Mapped[list["ArticleConfig"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
