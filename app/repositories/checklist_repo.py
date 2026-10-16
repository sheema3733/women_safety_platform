from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy import select, func
from app.database import db_session
from app.models.checklist import ChecklistItem, UserChecklistProgress

class ChecklistRepository:
    @staticmethod
    def get_all_items() -> List[ChecklistItem]:
        stmt = select(ChecklistItem).order_by(ChecklistItem.sort_order, ChecklistItem.id)
        return list(db_session.execute(stmt).scalars().all())

    @staticmethod
    def get_by_id(item_id: int) -> Optional[ChecklistItem]:
        return db_session.get(ChecklistItem, item_id)

    @staticmethod
    def create_item(title: str, description: str = "", category: str = "General", sort_order: int = 1) -> ChecklistItem:
        item = ChecklistItem(
            title=title.strip(),
            description=description.strip(),
            category=category.strip(),
            sort_order=sort_order
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    @staticmethod
    def get_user_progress(user_id: int) -> Dict[int, bool]:
        stmt = select(UserChecklistProgress).where(UserChecklistProgress.user_id == user_id)
        records = db_session.execute(stmt).scalars().all()
        return {r.item_id: r.is_completed for r in records}

    @staticmethod
    def toggle_item(user_id: int, item_id: int, is_completed: bool) -> UserChecklistProgress:
        stmt = select(UserChecklistProgress).where(
            UserChecklistProgress.user_id == user_id,
            UserChecklistProgress.item_id == item_id
        )
        progress = db_session.execute(stmt).scalars().first()
        if not progress:
            progress = UserChecklistProgress(
                user_id=user_id,
                item_id=item_id,
                is_completed=is_completed,
                completed_at=datetime.now(timezone.utc) if is_completed else None
            )
            db_session.add(progress)
        else:
            progress.is_completed = is_completed
            progress.completed_at = datetime.now(timezone.utc) if is_completed else None

        db_session.commit()
        db_session.refresh(progress)
        return progress

    @staticmethod
    def get_user_stats(user_id: int) -> dict:
        total_items = db_session.execute(select(func.count(ChecklistItem.id))).scalar() or 0
        if total_items == 0:
            return {"completed": 0, "total": 0, "percentage": 0}

        completed_count = db_session.execute(
            select(func.count(UserChecklistProgress.id)).where(
                UserChecklistProgress.user_id == user_id,
                UserChecklistProgress.is_completed.is_(True)
            )
        ).scalar() or 0

        pct = int(round((completed_count / total_items) * 100))
        return {
            "completed": completed_count,
            "total": total_items,
            "percentage": pct
        }

    @staticmethod
    def get_overall_stats() -> dict:
        total_items = db_session.execute(select(func.count(ChecklistItem.id))).scalar() or 0
        total_completions = db_session.execute(
            select(func.count(UserChecklistProgress.id)).where(UserChecklistProgress.is_completed.is_(True))
        ).scalar() or 0
        return {
            "total_items": total_items,
            "total_completions": total_completions
        }
