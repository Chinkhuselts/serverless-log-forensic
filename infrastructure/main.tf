provider "aws" {
  region = "eu-north-1"
}

# 1. S3 Bucket (Storage)
resource "aws_s3_bucket" "logs_bucket" {
  bucket_prefix = "web-logs-ingest-"
  force_destroy = true
}

# 2. DynamoDB (Database)
resource "aws_dynamodb_table" "threats" {
  name           = "ThreatsTable"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "AttackID"

  attribute {
    name = "AttackID"
    type = "S"
  }
}

# 3. IAM Role (Permissions)
resource "aws_iam_role" "processor_role" {
  name = "log_processor_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" } }]
  })
}

resource "aws_iam_policy" "processor_policy" {
  name = "log_processor_policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Action = ["s3:GetObject"], Effect = "Allow", Resource = "${aws_s3_bucket.logs_bucket.arn}/*" },
      { Action = ["dynamodb:PutItem", "dynamodb:BatchWriteItem"], Effect = "Allow", Resource = aws_dynamodb_table.threats.arn },
      { Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], Effect = "Allow", Resource = "*" }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.processor_role.name
  policy_arn = aws_iam_policy.processor_policy.arn
}

# 4. Lambda Function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "log_analyzer.py"
  output_path = "log_analyzer.zip"
}

resource "aws_lambda_function" "processor" {
  filename         = "log_analyzer.zip"
  function_name    = "LogThreatAnalyzer"
  role             = aws_iam_role.processor_role.arn
  handler          = "log_analyzer.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

# 5. Trigger
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.logs_bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.logs_bucket.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.processor.arn
    events              = ["s3:ObjectCreated:*"]
  }
  depends_on = [aws_lambda_permission.allow_s3]
}

# Outputs
output "bucket_name" { value = aws_s3_bucket.logs_bucket.id }