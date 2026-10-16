from typing import Optional, List, Tuple, Set
from datetime import datetime, timezone
from sqlalchemy import select, func, desc, or_
from app.database import db_session
from app.models.tip import SafetyTip, TipView

class TipRepository:
    @staticmethod
    def get_by_id(tip_id: int) -> Optional[SafetyTip]:
        return db_session.get(SafetyTip, tip_id)

    @staticmethod
    def create_tip(
        title: str,
        category: str,
        summary: str,
        content: str,
        read_time_minutes: int = 3,
        is_published: bool = True
    ) -> SafetyTip:
        tip = SafetyTip(
            title=title.strip(),
            category=category.strip(),
            summary=summary.strip(),
            content=content.strip(),
            read_time_minutes=read_time_minutes,
            is_published=is_published
        )
        db_session.add(tip)
        db_session.commit()
        db_session.refresh(tip)
        return tip

    @staticmethod
    def update_tip(tip: SafetyTip, **kwargs) -> SafetyTip:
        for key, val in kwargs.items():
            if hasattr(tip, key):
                setattr(tip, key, val)
        db_session.commit()
        db_session.refresh(tip)
        return tip

    @staticmethod
    def delete_tip(tip: SafetyTip) -> None:
        db_session.delete(tip)
        db_session.commit()

    @staticmethod
    def get_published_tips(search: str = "", category: str = "", limit: int = 50) -> List[SafetyTip]:
        stmt = select(SafetyTip).where(SafetyTip.is_published.is_(True))

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(SafetyTip.title).like(s),
                    func.lower(SafetyTip.summary).like(s),
                    func.lower(SafetyTip.content).like(s)
                )
            )

        if category:
            stmt = stmt.where(SafetyTip.category == category)

        stmt = stmt.order_by(SafetyTip.category, SafetyTip.title).limit(limit)
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def list_all_tips(
        search: str = "",
        category: str = "",
        status_filter: str = "",
        page: int = 1,
        per_page: int = 15
    ) -> Tuple[List[SafetyTip], int]:
        stmt = select(SafetyTip)

        if search:
            s = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(SafetyTip.title).like(s),
                    func.lower(SafetyTip.summary).like(s)
                )
            )

        if category:
            stmt = stmt.where(SafetyTip.category == category)

        if status_filter == "published":
            stmt = stmt.where(SafetyTip.is_published.is_(True))
        elif status_filter == "draft":
            stmt = stmt.where(SafetyTip.is_published.is_(False))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db_session.execute(count_stmt).scalar() or 0

        tips = list(db_session.execute(
            stmt.order_by(desc(SafetyTip.created_at)).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all())

        return tips, total

    @staticmethod
    def record_view(user_id: int, tip_id: int) -> bool:
        # Check if already recorded
        stmt = select(TipView).where(TipView.user_id == user_id, TipView.tip_id == tip_id)
        existing = db_session.execute(stmt).scalars().first()
        if not existing:
            view = TipView(user_id=user_id, tip_id=tip_id, viewed_at=datetime.now(timezone.utc))
            db_session.add(view)
            # Increment tip view count
            tip = db_session.get(SafetyTip, tip_id)
            if tip:
                tip.view_count += 1
            db_session.commit()
            return True
        return False

    @staticmethod
    def get_user_viewed_tip_ids(user_id: int) -> Set[int]:
        stmt = select(TipView.tip_id).where(TipView.user_id == user_id)
        return set(db_session.execute(stmt).scalars().all())

    @staticmethod
    def get_metrics() -> dict:
        total = db_session.execute(select(func.count(SafetyTip.id))).scalar() or 0
        published = db_session.execute(
            select(func.count(SafetyTip.id)).where(SafetyTip.is_published.is_(True))
        ).scalar() or 0
        total_views = db_session.execute(select(func.sum(SafetyTip.view_count))).scalar() or 0
        return {
            "total_tips": total,
            "published_tips": published,
            "total_views": total_views
        }
