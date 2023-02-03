terraform {
  cloud {
    organization = "kuzat-co"

    workspaces {
      name = "daily-dice-roller"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
  default_tags {
    tags = {
      env = "pro"
      service = terraform.workspace
    }
  }
}

resource "tls_private_key" "ssh_private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "diceRollSSHKey"
  public_key = tls_private_key.ssh_private_key.public_key_openssh

  provisioner "local-exec" {
    # Generate "terraform-key-pair.pem" in current directory
    command = <<-EOT
      echo '${tls_private_key.ssh_private_key.private_key_pem}' > ./'${aws_key_pair.ssh_key.key_name}'.pem
      chmod 400 ./'${aws_key_pair.ssh_key.key_name}'.pem
    EOT
  }
}

resource "aws_security_group" "diceServerSg" {
  name = "allow_ssh"
  description = "Allow inbound ssh connections"

  egress {
    from_port = 0
    protocol  = "-1"
    to_port   = 0
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port = 22
    protocol  = "TCP"
    to_port   = 22
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "allow_ssh"
  }
}

resource "aws_instance" "dice_server" {
  ami           = "ami-00c70b245f5354c0a"
  instance_type = "m5.large"
  key_name      = aws_key_pair.ssh_key.key_name
  security_groups = [aws_security_group.diceServerSg.name]
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name

  tags = {
    Name = "RollerDiceBot"
  }
}

resource "aws_s3_bucket" "backup_bucket" {
  bucket = "${terraform.workspace}-db-backup-pro"
}

resource "aws_s3_bucket_lifecycle_configuration" "backup_bucket_retention" {
  bucket = aws_s3_bucket.backup_bucket.bucket
  rule {
    id     = "30 days retention"
    expiration {
      days = 30
    }
    status = "Enabled"
  }
}


output "server_public_dns" {
  value = "ssh -i  ${aws_key_pair.ssh_key.key_name}.pem ubuntu@${aws_instance.dice_server.public_dns}"
}

output "backup_s3_bucket" {
  value = aws_s3_bucket.backup_bucket.bucket
}
