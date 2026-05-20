terraform {
  required_providers {
    keycloak = {
      source = "keycloak/keycloak"
    }
  }
}

# ---------------------------------------------
# Realm Roles
# ---------------------------------------------

variable "roles" {
  description = "Map of realm roles and their descriptions"
  type        = map(string)

  default = {
    read-all-records-role = <<EOT
Allows users to read all records in the system, regardless of the organization they belong to.
EOT

    write-all-records-role = <<EOT
Allows users to create, update, or delete any record in the system, regardless of organization.
EOT

    read-organization-records-role = <<EOT
Allows users to read records belonging to their own organization only.
EOT

    write-organization-records-role = <<EOT
Allows users to create, update, or delete records within their own organization only.
EOT

    complete-records-role = <<EOT
Allows users to mark records as complete.
EOT

    reject-records-role = <<EOT
Allows users to reject records.
EOT

    publish-records-role = <<EOT
Allows users to publish records.
EOT

    import-codelists-role = <<EOT
Allows users to import codelists into the system.
EOT

    comment-record-questions-role = <<EOT
Allows users to add comments to questions in records.
EOT

    read-all-users-role = <<EOT
Allows users to view the details of all users in the system.
EOT

    write-all-users-role = <<EOT
Allows users to create, update, or delete any user account in the system.
EOT

    read-organization-users-role = <<EOT
Allows users to view users within their own organization only.
EOT

    write-organization-users-role = <<EOT
Allows users to manage users within their own organization only.
EOT

    read-organization-role = <<EOT
Allows users to view their own organization details.
EOT

    write-organization-role = <<EOT
Allows users to modify their own organization details.
EOT

    read-all-organizations-role = <<EOT
Allows users to view all organizations in the system.
EOT

    write-all-organizations-role = <<EOT
Allows users to manage all organizations.
EOT

    read-action-history-role = <<EOT
Allows users to view system action history.
EOT

    read-statistics-role = <<EOT
Allows users to view statistical reports.
EOT

    read-media-role = <<EOT
Allows users to view embedded media content such as images and videos served by MediaCMS.
EOT

    write-media-role = <<EOT
Allows users to upload and manage their own media assets in MediaCMS.
EOT

    admin-media-role = <<EOT
Allows users full administrative access to MediaCMS including managing all users and content.
EOT

    annotator-access-role = <<EOT
Allows users to access the media asset annotator.
EOT
    read-answer-feedback-role = <<EOT
Allows users to view feedback for entered answers.
EOT
    read-question-hint-role = <<EOT
Allows users to reveal hint for question.
EOT
  }
}

resource "keycloak_role" "realm_roles" {
  for_each = var.roles

  realm_id    = var.realm_id
  name        = each.key
  description = trimspace(each.value)
}

# ---------------------------------------------
# Impersonation Composite Role
# ---------------------------------------------

data "keycloak_openid_client" "realm_management" {
  realm_id  = var.realm_id
  client_id = "realm-management"
}

data "keycloak_role" "realm_management_impersonation" {
  realm_id  = var.realm_id
  client_id = data.keycloak_openid_client.realm_management.id
  name      = "impersonation"
}

resource "keycloak_role" "impersonate_role_composite" {
  realm_id = var.realm_id
  name     = "impersonate-role"

  composite_roles = [
    data.keycloak_role.realm_management_impersonation.id
  ]
}