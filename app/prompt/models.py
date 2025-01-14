from database import db
from sqlalchemy.orm import Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..auth.models import Users

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return '<Prompt %r>' % self.title

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

