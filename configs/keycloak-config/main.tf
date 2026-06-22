terraform {
  required_providers {
    keycloak = {
      source  = "keycloak/keycloak"
      version = "5.7.0"
    }
  }
}

provider "keycloak" {
  client_id = "admin-cli"
  username  = var.kc_admin_user
  password  = var.kc_admin_password
  url       = var.kc_url
}

module "realms" {
  source = "./modules/realms"
  kc_realm                  = var.kc_realm
  kc_access_token_lifespan  = var.kc_access_token_lifespan
}

module "clients" {
  source = "./modules/clients"
  realm_id            = module.realms.realm_id
  mediacms_base_url   = var.mediacms_base_url
  public_origin       = var.public_origin
  base_path           = var.base_path
  rm_base_path        = var.rm_base_path
}

module "roles" {
  source   = "./modules/roles"
  realm_id = module.realms.realm_id
}

module "scopes" {
  source = "./modules/scopes"
  realm_id            = module.realms.realm_id
  mediacms_client_id  = module.clients.mediacms_client_id
  annotator_client_id = module.clients.annotator_client_id
}

module "role_groups" {
  source = "./modules/role-groups"
  realm_id       = module.realms.realm_id
  realm_role_ids = module.roles.realm_role_ids
}

module "events" {
  source   = "./modules/events"
  realm_id = module.realms.realm_id
  events_enabled               = false
  admin_events_enabled         = false
  admin_events_details_enabled = false
}

module "identity_providers" {
  source = "./modules/identity-providers"
  realm_id             = module.realms.realm_id
  enable_google        = var.enable_google_login
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret
}

