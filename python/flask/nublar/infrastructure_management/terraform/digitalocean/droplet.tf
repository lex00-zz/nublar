variable "do_image" {}
variable "app_name" {}
variable "app_port" {}
variable "do_region" {}
variable "do_size" {}
variable "do_ssh_keys" {}

resource "digitalocean_droplet" "web" {
  count  = 1
  image  = "${var.do_image}"
  name   = "${var.app_name}"
  region = "${var.do_region}"
  size   = "${var.do_size}"
  ssh_keys = ["${var.do_ssh_keys}"]
}

resource "digitalocean_firewall" "web" {
  name = "web"

  droplet_ids = ["${digitalocean_droplet.web.id}"]

  inbound_rule = [
    {
      protocol           = "tcp"
      port_range         = "22"
      source_addresses   = ["0.0.0.0/0", "::/0"]
    },
    {
      protocol           = "tcp"
      port_range         = "${var.app_port}"
      source_addresses   = ["0.0.0.0/0", "::/0"]
    }
  ]

  outbound_rule {
    protocol                = "udp"
    port_range              = "53"
    destination_addresses   = ["0.0.0.0/0", "::/0"]
  }
}
