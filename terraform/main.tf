terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# ── Variables ──────────────────────────────────────────────
variable "location" {
  default = "West Europe"
}

variable "project_name" {
  default = "incident-sync"
}

# ── Resource Group ─────────────────────────────────────────
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = var.location
}

# ── Storage Account (needed by Azure Functions) ────────────
resource "azurerm_storage_account" "main" {
  name                     = "incidentsyncstore"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# ── Blob Container (stores incident summaries as JSON) ──────
resource "azurerm_storage_container" "incidents" {
  name                  = "incident-summaries"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# ── App Service Plan (serverless/consumption) ──────────────
resource "azurerm_service_plan" "main" {
  name                = "${var.project_name}-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "Y1"  # Consumption plan (pay-per-use)
}

# ── Azure Function App ─────────────────────────────────────
resource "azurerm_linux_function_app" "main" {
  name                = "${var.project_name}-fn"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key
  service_plan_id            = azurerm_service_plan.main.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "DATABASE_URL"             = var.database_url
    "SLACK_WEBHOOK_URL"        = var.slack_webhook_url
  }
}

# ── API Management ─────────────────────────────────────────
resource "azurerm_api_management" "main" {
  name                = "${var.project_name}-apim"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "Incident Sync Team"
  publisher_email     = "admin@example.com"
  sku_name            = "Consumption_0"  # Free tier
}

# ── Outputs ────────────────────────────────────────────────
output "function_app_url" {
  value = "https://${azurerm_linux_function_app.main.default_hostname}/api/incidents"
}

output "apim_gateway_url" {
  value = azurerm_api_management.main.gateway_url
}
