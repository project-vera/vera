# Configure the AWS provider
provider "aws" {
  region = "eu-west-1"
}

# Create an EC2 instance
resource "aws_instance" "example" {
  ami           = "ami-13095cba0d3649579"
  instance_type = "t2.micro"
  
  tags = {
    Name = "terraform-example"
  }
}
