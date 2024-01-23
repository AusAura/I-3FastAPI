import enum
from datetime import date
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Boolean, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    created_at: Mapped[date] = mapped_column("created_at", DateTime(timezone=True), default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime(timezone=True), default=func.now(),
                                             onupdate=func.now())
    about: Mapped[str] = mapped_column(String(500), nullable=True)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    publications = relationship("Publication", secondary="publication_tag", back_populates="tags", lazy="joined")


class PublicationTagAssociation(Base):
    __tablename__ = "publication_tag"

    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", backref="publications", lazy="joined")

    image: Mapped["PubImage"] = relationship("PubImage", backref="publications", lazy="joined", uselist=False,
                                             cascade="all,delete")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="publication", lazy="joined",
                                              cascade="all,delete")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="publication_tag", back_populates="publications",
                                             lazy="joined")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="publication", lazy="joined",
                                                   cascade="all, delete")

    created_at: Mapped[date] = mapped_column("created_at", DateTime(timezone=True), default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime(timezone=True), default=func.now(),
                                             onupdate=func.now())

    @property
    def average_rating(self) -> Optional[float]:
        if self.ratings:
            if len(self.ratings) == 0:  # type: ignore
                return None
            return sum(rating.score for rating in self.ratings) / len(self.ratings)  # type: ignore
        return None


class PubImage(Base):
    __tablename__ = "pub_images"

    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"), nullable=True)
    id: Mapped[int] = mapped_column(primary_key=True)
    current_img: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_img: Mapped[str] = mapped_column(String(255), default=None, nullable=True)
    qr_code_img: Mapped[str] = mapped_column(String(255), default=None, nullable=True)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", backref="comments", lazy="joined")
    text: Mapped[str] = mapped_column(String(250), nullable=False)

    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"))
    publication: Mapped["Publication"] = relationship("Publication", back_populates="comment", lazy="joined")

    # emoji: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user) # reaction with the comment?

    created_at: Mapped[date] = mapped_column("created_at", DateTime(timezone=True), default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime(timezone=True), default=func.now(),
                                             onupdate=func.now())


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"))
    score: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'publication_id', name='uix_1'),
        CheckConstraint('score >= 1 AND score <= 5', name='check_score_range')
    )

    user: Mapped["User"] = relationship("User", backref="ratings", lazy="joined")
    publication: Mapped["Publication"] = relationship("Publication", back_populates="ratings", lazy="joined")

    @validates('score')
    def validate_score(self, key, score):
        if not (1 <= score <= 5):
            raise ValueError("Score must be between 1 and 5")
        return score
