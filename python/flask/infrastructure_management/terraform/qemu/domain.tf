variable "qemu_memory" {}
variable "qemu_cpus" {}

resource "libvirt_network" "tf" {
   name = "tf"
   domain = "tf.local"
   mode = "nat"
   addresses = ["10.0.100.0/24"]
}

resource "libvirt_volume" "flask_github_jobs" {
  name = "flask_github_jobs"
  source = "../../../imaging/packer/qemu/packer_output/flask-github-jobs.qcow2"
}

resource "libvirt_domain" "flask_github_jobs" {
  name = "flask_github_jobs"
  memory = "${var.qemu_memory}"
  vcpu = "${var.qemu_cpus}"
  network_interface {
      network_name = "tf"
  }
  disk {
       volume_id = "${libvirt_volume.flask_github_jobs.id}"
  }
}
