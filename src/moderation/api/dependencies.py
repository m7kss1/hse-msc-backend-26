from moderation.repositories.policies import InMemoryPolicyRepository
from moderation.services.moderation import ModerationService


def get_moderation_service() -> ModerationService:
    return ModerationService(repository=InMemoryPolicyRepository())
