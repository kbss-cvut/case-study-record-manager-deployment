from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class RoleRestrictedSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        claims = sociallogin.account.extra_data or {}
        roles = claims.get("realm_access", {}).get("roles", [])

        role_mapping = getattr(settings, "MEDIACMS_ROLE_MAPPING", {})
        if not any(r in role_mapping for r in roles):
            logger.warning(
                "[Access denied] User %s has no recognized media role.",
                claims.get("preferred_username"),
            )
            raise PermissionDenied("Missing required media role.")

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        claims = sociallogin.account.extra_data or {}
        keycloak_roles = claims.get("realm_access", {}).get("roles", [])

        role_mapping = getattr(settings, "MEDIACMS_ROLE_MAPPING", {})
        role_priority = getattr(settings, "MEDIACMS_ROLE_PRIORITY", [])

        # Pick highest priority role the user has
        mediacms_role = None
        for keycloak_role in role_priority:
            if keycloak_role in keycloak_roles:
                mediacms_role = role_mapping[keycloak_role]
                break

        if mediacms_role:
            logger.info(
                "[OIDC] Mapping user %s to MediaCMS role '%s'",
                user.username,
                mediacms_role,
            )
            user.set_role_from_mapping(mediacms_role)

        return user