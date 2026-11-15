from typing import Protocol

from moderation.domain.models import ModerationPolicy


class PolicyRepository(Protocol):
    def get_policy(self) -> ModerationPolicy: ...


class InMemoryPolicyRepository:
    def __init__(self, policy: ModerationPolicy | None = None) -> None:
        self._policy = policy if policy is not None else ModerationPolicy()

    def get_policy(self) -> ModerationPolicy:
        return self._policy
