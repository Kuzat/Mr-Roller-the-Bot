resource "aws_iam_policy" "ec2_policy" {
  name        = "roller_bot_ec2_policy"
  path        = "/"
  description = "A policy to provide permissions to the EC2 server for roller bot"
  policy      = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect : "Allow",
        Action : [
          "s3:*"
        ],
        Resource : [
          aws_s3_bucket.backup_bucket.arn,
          "${aws_s3_bucket.backup_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "ec2_role" {
  name               = "roller_bot_ec2_role"
  assume_role_policy = jsonencode({
    Version : "2012-10-17",
    Statement : [
      {
        Effect : "Allow",
        Action : "sts:AssumeRole",
        Sid : "",
        Principal : {
          Service : "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "ec2_policy_role" {
  name       = "ec2_attachment"
  roles = [aws_iam_role.ec2_role.name]
  policy_arn = aws_iam_policy.ec2_policy.arn
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_profile"
  role = aws_iam_role.ec2_role.name
}
