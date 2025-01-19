from database import db
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from ..auth.models import Users

class ArticleConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    search_engine = db.Column(db.String(10), nullable=False, default="google")
    gpt = db.Column(db.String(10), nullable=False, default="erniebot")
    networking_RAG = db.Column(db.Boolean, nullable=False,default=True)
    local_RAG = db.Column(db.Boolean, nullable=False, default=False)
    step_by_step = db.Column(db.Boolean, nullable=False, default=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user: Mapped["Users"] = relationship(back_populates="article_configs")
    local_RAG_files: Mapped[list["UserFile"]] = relationship(
      back_populates="article_config",
      cascade="all, delete-orphan"
    )
    article_prompt: Mapped["ArticlePrompt"] = relationship(back_populates="article_config", cascade="all, delete-orphan")
    
    def to_dict(self):
      return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    
class UserFile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(64), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    
    config_id = db.Column(db.Integer, db.ForeignKey('article_config.id'), nullable=False)
    article_config: Mapped["ArticleConfig"] = relationship(back_populates="local_RAG_files")
    

class ArticlePrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    config_id = db.Column(db.Integer, db.ForeignKey('article_config.id'), nullable=False)
    
    article_config: Mapped["ArticleConfig"] = relationship(back_populates="article_prompt")
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
