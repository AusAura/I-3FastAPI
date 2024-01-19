import enum
from datetime import date
from typing import List


from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Boolean
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

    publications = relationship("Publication", secondary="publication_tag", back_populates="tags")


class PublicationTagAssociation(Base):
    __tablename__ = "publication_tag"

    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", backref="publications", lazy="joined")

    # cls PubImage  __tablename__ = "pub_images"   OneToOne relationship

    image: Mapped["PubImage"] = relationship("PubImage", backref="publications", lazy="joined", uselist=False)
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="publication_tag", back_populates="publications")

    comment: Mapped["Comment"] = relationship("Comment", back_populates="publication")

    # # cls Rating  __tablename__ = "ratings"  OneToMany relationship
    # rating: Mapped["Rating"] = relationship("Rating", back_populates="publications")

    created_at: Mapped[date] = mapped_column("created_at", DateTime(timezone=True), default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime(timezone=True), default=func.now(),
                                             onupdate=func.now())


class PubImage(Base):
    __tablename__ = "pub_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"), nullable=True)

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
