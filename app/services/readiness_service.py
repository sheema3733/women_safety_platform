from typing import Dict, Any
from app.repositories.contact_repo import ContactRepository
from app.repositories.checklist_repo import ChecklistRepository
from app.repositories.tip_repo import TipRepository
from app.repositories.user_repo import UserRepository

READINESS_DISCLAIMER = (
    "Safety Readiness reflects preparedness activities completed on the platform. "
    "It does not guarantee personal safety."
)

class ReadinessService:
    @staticmethod
    def calculate_score(user_id: int) -> Dict[str, Any]:
        user = UserRepository.get_by_id(user_id)
        if not user:
            return {
                "score": 0,
                "level": "Basic Preparedness",
                "breakdown": {},
                "disclaimer": READINESS_DISCLAIMER
            }

        # 1. Contacts Score (Max 30)
        contacts = ContactRepository.get_for_user(user_id)
        contacts_count = len(contacts)
        has_trusted = any(c.is_trusted for c in contacts)

        if contacts_count >= 3:
            contact_score = 25
        elif contacts_count == 2:
            contact_score = 20
        elif contacts_count == 1:
            contact_score = 10
        else:
            contact_score = 0

        if has_trusted and contact_score > 0:
            contact_score = min(30, contact_score + 5)

        # 2. Checklist Progress Score (Max 40)
        checklist_stats = ChecklistRepository.get_user_stats(user_id)
        pct = checklist_stats.get("percentage", 0)
        checklist_score = int(round((pct / 100.0) * 40))

        # 3. Safety Tips Viewed (Max 15)
        viewed_tip_ids = TipRepository.get_user_viewed_tip_ids(user_id)
        tips_viewed_count = len(viewed_tip_ids)
        tips_score = min(15, tips_viewed_count * 3)

        # 4. Profile & Resource Preparation (Max 15)
        profile_score = 0
        if user.phone and len(user.phone.strip()) >= 7:
            profile_score += 5
        if user.city and len(user.city.strip()) >= 2:
            profile_score += 5
        if tips_viewed_count > 0 or contacts_count > 0:
            profile_score += 5

        total_score = min(100, contact_score + checklist_score + tips_score + profile_score)

        if total_score >= 85:
            level = "Optimum Preparedness"
            color = "forest-mint"
        elif total_score >= 60:
            level = "High Preparedness"
            color = "forest-mint"
        elif total_score >= 35:
            level = "Moderate Preparedness"
            color = "warm-plum"
        else:
            level = "Basic Preparedness"
            color = "muted-coral"

        return {
            "score": total_score,
            "level": level,
            "badge_color": color,
            "disclaimer": READINESS_DISCLAIMER,
            "breakdown": {
                "contacts": {
                    "earned": contact_score,
                    "max": 30,
                    "count": contacts_count,
                    "has_trusted": has_trusted
                },
                "checklist": {
                    "earned": checklist_score,
                    "max": 40,
                    "completed": checklist_stats.get("completed", 0),
                    "total": checklist_stats.get("total", 0),
                    "percentage": pct
                },
                "tips": {
                    "earned": tips_score,
                    "max": 15,
                    "viewed_count": tips_viewed_count
                },
                "profile": {
                    "earned": profile_score,
                    "max": 15,
                    "has_phone": bool(user.phone),
                    "has_city": bool(user.city)
                }
            }
        }
