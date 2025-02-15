from database import db
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Mapped, relationship

class Prompt(db.Model):
    """
    Prompt for article polish, optimization, etc.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return '<Prompt %r>' % self.title

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class TemplateOption(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    prompt = db.Column(db.Text)
    
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    template: Mapped["Template"] = relationship(
        back_populates="options"
    )
    
    def __repr__(self):
        return '<Prompt %r>' % self.title

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Template(db.Model):
    """
    Templates for erniebot article generating assistant.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(64), nullable=False)
    icon = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    options: Mapped[list["TemplateOption"]] = relationship(
        back_populates="template", 
        cascade="all, delete-orphan"
    )