terraform {
  required_providers {
    keycloak = {
      source = "keycloak/keycloak"
    }
  }
}

# -------------------------------------------------------
# Role Group Definitions
# -------------------------------------------------------

locals {
  role_groups = {
    admin-role-group = [
      "read-all-records-role",
      "write-all-records-role",
      "read-organization-records-role",
      "write-organization-records-role",
      "complete-records-role",
      "reject-records-role",
      "publish-records-role",
      "import-codelists-role",
      "comment-record-questions-role",
      "read-all-users-role",
      "write-all-users-role",
      "read-organization-users-role",
      "write-organization-users-role",
      "read-organization-role",
      "write-organization-role",
      "read-all-organizations-role",
      "write-all-organizations-role",
      "read-action-history-role",
      "read-statistics-role",
      "read-media-role",
      "write-media-role",
      "admin-media-role",
      "annotator-access-role"
    ]

    data-collection-coordinator-role-group = [
      "read-all-users-role",
      "write-all-users-role",
      "read-organization-users-role",
      "write-organization-users-role",
      "read-organization-role",
      "write-organization-role",
      "read-all-organizations-role",
      "write-all-organizations-role",
      "read-organization-records-role",
      "write-organization-records-role",
      "comment-record-questions-role",
      "complete-records-role",
      "annotator-access-role"
    ]

    organization-manager-role-group = [
      "read-organization-role",
      "write-organization-role",
      "read-organization-users-role",
      "write-organization-users-role",
      "read-organization-records-role",
      "write-organization-records-role",
      "comment-record-questions-role"
    ]

    entry-clerk-role-group = [
      "read-organization-role",
      "read-organization-records-role",
      "comment-record-questions-role"
    ]

    reviewer-role-group = [
      "complete-records-role",
      "comment-record-questions-role"
    ]
  }

  all_roles = distinct(flatten(values(local.role_groups)))
}

# -------------------------------------------------------
# Create Groups
# -------------------------------------------------------

resource "keycloak_group" "groups" {
  for_each = local.role_groups

  realm_id = var.realm_id
  name     = each.key
}

# -------------------------------------------------------
# Assign Roles To Groups
# -------------------------------------------------------
resource "keycloak_group_roles" "group_role_assignments" {
  for_each = local.role_groups

  realm_id = var.realm_id
  group_id = keycloak_group.groups[each.key].id

  role_ids = [
    for role_name in each.value :
    var.realm_role_ids[role_name]
  ]
}