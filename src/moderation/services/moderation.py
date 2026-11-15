from moderation.domain.models import Listing
from moderation.repositories.policies import PolicyRepository


class ModerationService:
    def __init__(self, repository: PolicyRepository) -> None:
        self._repository = repository

    def predict(self, listing: Listing) -> bool:
        """Возвращает True при наличии нарушений"""
        if listing.is_verified_seller:
            return False

        policy = self._repository.get_policy()
        return listing.images_qty < policy.minimum_images
