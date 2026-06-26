# Configure the AWS provider
provider "aws" {
  region = "eu-west-1"
}

# Create a Security Group for an EC2 instance 
resource "aws_security_group" "instance" {
  name = "terraform-example-instance"
  
  ingress {
    from_port	  = "${var.server_port}"
    to_port	    = "${var.server_port}"
    protocol	  = "tcp"
    cidr_blocks	= ["0.0.0.0/0"]
  }
}

# Create an EC2 instance
resource "aws_instance" "example" {
  ami			                = "ami-13095cba0d3649579"
  instance_type           = "t2.micro"
  vpc_security_group_ids  = ["${aws_security_group.instance.id}"]
  
  user_data = <<-EOF
	      #!/bin/bash
	      echo "Hello, World" > index.html
	      nohup busybox httpd -f -p "${var.server_port}" &
	      EOF
			  
  tags = {
    Name = "terraform-example"
  }
}
