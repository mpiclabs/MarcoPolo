terraform {
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "2.11.4"
    }
  }
}

# Configure the Vultr Provider
provider "vultr" {
  rate_limit  = 700
  retry_limit = 3
}

# control which 
variable "create_instances" {
  description = "A map of instances to be created with boolean values"
  type        = map(bool)
  default     = {
    "instance1" = false
    "instance2" = false
    "instance3" = false
  }
}

# Create an instance
resource "vultr_instance" "vultramsterdam" {
  plan             = "vc2-2c-4gb"
  region           = "ams"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultramsterdam"
  hostname         = "vultramsterdam"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultratlanta" {
  plan             = "vc2-2c-4gb"
  region           = "atl"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultratlanta"
  hostname         = "vultratlanta"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrchicago" {
  plan             = "vc2-2c-4gb"
  region           = "ord"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrchicago"
  hostname         = "vultrchicago"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrdallas" {
  plan             = "vc2-2c-4gb"
  region           = "dfw"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrdallas"
  hostname         = "vultrdallas"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrfrankfurt" {
  plan             = "vc2-2c-4gb"
  region           = "fra"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrfrankfurt"
  hostname         = "vultrfrankfurt"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrlondon" {
  plan             = "vc2-2c-4gb"
  region           = "lhr"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrlondon"
  hostname         = "vultrlondon"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrmadrid" {
  plan             = "vc2-2c-4gb"
  region           = "mad"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrmadrid"
  hostname         = "vultrmadrid"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrmelbourne" {
  plan             = "vc2-2c-4gb"
  region           = "mel"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrmelbourne"
  hostname         = "vultrmelbourne"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrmexicocity" {
  plan             = "vc2-2c-4gb"
  region           = "mex"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrmexicocity"
  hostname         = "vultrmexicocity"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrmiami" {
  plan             = "vc2-2c-4gb"
  region           = "mia"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrmiami"
  hostname         = "vultrmiami"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrmumbai" {
  plan             = "vc2-2c-4gb"
  region           = "bom"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrmumbai"
  hostname         = "vultrmumbai"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrbangalore" {
  plan             = "vc2-2c-4gb"
  region           = "blr"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrbangalore"
  hostname         = "vultrbangalore"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrparis" {
  plan             = "vc2-2c-4gb"
  region           = "cdg"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrparis"
  hostname         = "vultrparis"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrsaopaulo" {
  plan             = "vc2-1c-2gb-sc1"
  region           = "sao"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrsaopaulo"
  hostname         = "vultrsaopaulo"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrseattle" {
  plan             = "vc2-2c-4gb"
  region           = "sea"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrseattle"
  hostname         = "vultrseattle"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrseoul" {
  plan             = "vc2-2c-4gb"
  region           = "icn"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrseoul"
  hostname         = "vultrseoul"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrsiliconvalley" {
  plan             = "vc2-2c-4gb"
  region           = "sjc"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrsiliconvalley"
  hostname         = "vultrsiliconvalley"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrsingapore" {
  plan             = "vc2-2c-4gb"
  region           = "sgp"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrsingapore"
  hostname         = "vultrsingapore"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}



resource "vultr_instance" "vultrstockholm" {
  plan             = "vc2-2c-4gb"
  region           = "sto"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrstockholm"
  hostname         = "vultrstockholm"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrsydney" {
  plan             = "vc2-2c-4gb"
  region           = "syd"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrsydney"
  hostname         = "vultrsydney"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrtokyo" {
  plan             = "vc2-2c-4gb"
  region           = "nrt"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrtokyo"
  hostname         = "vultrtokyo"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}

resource "vultr_instance" "vultrtoronto" {
  plan             = "vc2-2c-4gb"
  region           = "yto"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrtoronto"
  hostname         = "vultrtoronto"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrla" {
  plan             = "vc2-2c-4gb"
  region           = "lax"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrla"
  hostname         = "vultrla"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}




resource "vultr_instance" "vultrwarsaw" {
  plan             = "vc2-2c-4gb"
  region           = "waw"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrwarsaw"
  hostname         = "vultrwarsaw"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrnj2" {
  plan             = "vc2-2c-4gb"
  region           = "ewr"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrnj2"
  hostname         = "vultrnj2"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}


resource "vultr_instance" "vultrjohannesburg" {
  plan             = "vhp-2c-4gb-intel"
  region           = "jnb"
  os_id            = 1743
  ssh_key_ids      = ["1a35c663-f363-4ef0-9861-65781c3e1431"]
  backups          = "disabled"
  label            = "vultrjohannesburg"
  hostname         = "vultrjohannesburg"
  enable_ipv6      = true
  ddos_protection  = false
  activation_email = false
}
