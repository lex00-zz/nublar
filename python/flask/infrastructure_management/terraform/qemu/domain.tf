resource "libvirt_volume" "flask_github_jobs" {
  name = "flask_github_jobs"
  source = "../../../imaging/packer/qemu/packer_output/flask-github-jobs.qcow2"
}

resource "libvirt_domain" "flask_github_jobs" {
  name = "flask_github_jobs"
  disk {
       volume_id = "${libvirt_volume.flask_github_jobs.id}"
  }
}
