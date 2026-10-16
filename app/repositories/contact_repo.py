from typing import Optional, List
from sqlalchemy import select, func
from app.database import db_session
from app.models.contact import EmergencyContact

class ContactRepository:
    @staticmethod
    def get_by_id(contact_id: int) -> Optional[EmergencyContact]:
        return db_session.get(EmergencyContact, contact_id)

    @staticmethod
    def get_for_user(user_id: int) -> List[EmergencyContact]:
        stmt = (
            select(EmergencyContact)
            .where(EmergencyContact.user_id == user_id)
            .order_by(EmergencyContact.priority_order, EmergencyContact.name)
        )
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def get_trusted_for_user(user_id: int) -> List[EmergencyContact]:
        stmt = (
            select(EmergencyContact)
            .where(EmergencyContact.user_id == user_id, EmergencyContact.is_trusted.is_(True))
            .order_by(EmergencyContact.priority_order)
        )
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def create_contact(
        user_id: int,
        name: str,
        relationship: str,
        phone: str,
        is_trusted: bool = False,
        priority_order: int = 1
    ) -> EmergencyContact:
        contact = EmergencyContact(
            user_id=user_id,
            name=name.strip(),
            relationship=relationship.strip(),
            phone=phone.strip(),
            is_trusted=is_trusted,
            priority_order=priority_order
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)
        return contact

    @staticmethod
    def update_contact(contact: EmergencyContact, **kwargs) -> EmergencyContact:
        for key, val in kwargs.items():
            if hasattr(contact, key):
                setattr(contact, key, val)
        db_session.commit()
        db_session.refresh(contact)
        return contact

    @staticmethod
    def delete_contact(contact: EmergencyContact) -> None:
        db_session.delete(contact)
        db_session.commit()

    @staticmethod
    def count_for_user(user_id: int) -> int:
        stmt = select(func.count(EmergencyContact.id)).where(EmergencyContact.user_id == user_id)
        return db_session.execute(stmt).scalar() or 0
