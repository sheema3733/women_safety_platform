from typing import Optional, List, Tuple
from sqlalchemy import select, func, desc, or_
from app.database import db_session
from app.models.resource import EmergencyResource

class ResourceRepository:
    @staticmethod
    def get_by_id(resource_id: int) -> Optional[EmergencyResource]:
        return db_session.get(EmergencyResource, resource_id)

    @staticmethod
    def create_resource(
        name: str,
        category: str,
        city: str,
        general_area: str,
        demo_phone: str,
        description: str = "",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        is_active: bool = True
    ) -> EmergencyResource:
        resource = EmergencyResource(
            name=name.strip(),
            category=category.strip(),
            city=city.strip(),
            general_area=general_area.strip(),
            demo_phone=demo_phone.strip(),
            description=description.strip(),
            latitude=latitude,
            longitude=longitude,
            is_active=is_active
        )
        db_session.add(resource)
        db_session.commit()
        db_session.refresh(resource)
        return resource

    @staticmethod
    def update_resource(resource: EmergencyResource, **kwargs) -> EmergencyResource:
        for key, val in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, val)
        db_session.commit()
        db_session.refresh(resource)
        return resource

    @staticmethod
    def delete_resource(resource: EmergencyResource) -> None:
        db_session.delete(resource)
        db_session.commit()

    @staticmethod
    def get_active_resources(
        search: str = "",
        category: str = "",
        city: str = "",
        limit: int = 50
    ) -> List[EmergencyResource]:
        stmt = select(EmergencyResource).where(EmergencyResource.is_active.is_(True))

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(EmergencyResource.name).like(s),
                    func.lower(EmergencyResource.general_area).like(s),
                    func.lower(EmergencyResource.description).like(s)
                )
            )

        if category:
            stmt = stmt.where(EmergencyResource.category == category)
        if city:
            stmt = stmt.where(func.lower(EmergencyResource.city) == city.strip().lower())

        stmt = stmt.order_by(EmergencyResource.city, EmergencyResource.category, EmergencyResource.name).limit(limit)
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def list_all_resources(
        search: str = "",
        category: str = "",
        city: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 15
    ) -> Tuple[List[EmergencyResource], int]:
        stmt = select(EmergencyResource)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(EmergencyResource.name).like(s),
                    func.lower(EmergencyResource.general_area).like(s),
                    func.lower(EmergencyResource.city).like(s)
                )
            )

        if category:
            stmt = stmt.where(EmergencyResource.category == category)
        if city:
            stmt = stmt.where(func.lower(EmergencyResource.city) == city.strip().lower())

        if status_filter == "active":
            stmt = stmt.where(EmergencyResource.is_active.is_(True))
        elif status_filter == "inactive":
            stmt = stmt.where(EmergencyResource.is_active.is_(False))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        resources = list(db_session.execute(
            stmt.order_by(desc(EmergencyResource.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return resources, total

    @staticmethod
    def get_distinct_cities() -> List[str]:
        stmt = select(EmergencyResource.city).distinct().order_by(EmergencyResource.city)
        return [r for r in db_session.execute(stmt).scalars().all() if r]

    @staticmethod
    def get_metrics() -> dict:
        total = db_session.execute(select(func.count(EmergencyResource.id))).scalar() or 0
        active = db_session.execute(
            select(func.count(EmergencyResource.id)).where(EmergencyResource.is_active.is_(True))
        ).scalar() or 0
        return {
            "total_resources": total,
            "active_resources": active
        }
