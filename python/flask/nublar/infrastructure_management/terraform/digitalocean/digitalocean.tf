variable "do_image" {}
variable "app_name" {}
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
