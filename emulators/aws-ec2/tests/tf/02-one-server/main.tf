# Configure the AWS provider
provider "aws" {
  region = "eu-west-1"
}

# Create an EC2 instance
resource "aws_instance" "example" {
  ami           = "ami-0f9fc25dd2506cf6d"
  instance_type = "t2.micro"
  
  tags = {
    Name = "terraform-example"
  }
}
