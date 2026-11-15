from dataclasses import replace
from unittest.mock import Mock

import pytest

from moderation.domain.models import Listing, ModerationPolicy
from moderation.repositories.policies import InMemoryPolicyRepository, PolicyRepository
from moderation.services.moderation import ModerationService


@pytest.mark.parametrize(
    ("verified", "images", "has_violations"),
    [
        (True, 0, False),
        (True, 1, False),
        (True, 10, False),
        (False, 0, True),
        (False, 1, False),
        (False, 10, False),
    ],
)
def test_moderation_rules(
    listing: Listing, verified: bool, images: int, has_violations: bool
) -> None:
    service = ModerationService(InMemoryPolicyRepository())

    result = service.predict(replace(listing, is_verified_seller=verified, images_qty=images))

    assert result is has_violations


@pytest.mark.parametrize(("images", "has_violations"), [(1, True), (2, False), (3, False)])
def test_service_uses_repository_policy(
    listing: Listing, images: int, has_violations: bool
) -> None:
    repository = InMemoryPolicyRepository(ModerationPolicy(minimum_images=2))
    service = ModerationService(repository)

    assert service.predict(replace(listing, images_qty=images)) is has_violations


def test_verified_seller_does_not_require_policy_lookup(listing: Listing) -> None:
    repository = Mock(spec=PolicyRepository)
    repository.get_policy.side_effect = RuntimeError("Policy storage is unavailable")
    service = ModerationService(repository)

    assert service.predict(replace(listing, is_verified_seller=True)) is False
    repository.get_policy.assert_not_called()


def test_repository_failure_propagates_to_http_boundary(listing: Listing) -> None:
    repository = Mock(spec=PolicyRepository)
    repository.get_policy.side_effect = RuntimeError("Policy storage is unavailable")
    service = ModerationService(repository)

    with pytest.raises(RuntimeError, match="Policy storage is unavailable"):
        service.predict(listing)
