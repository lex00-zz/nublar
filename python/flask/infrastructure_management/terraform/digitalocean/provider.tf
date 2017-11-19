variable "DIGITALOCEAN_TOKEN" {}

provider "digitalocean" {
  token = "${var.DIGITALOCEAN_TOKEN}"
}
