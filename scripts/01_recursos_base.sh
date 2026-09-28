#!/bin/bash
# Recrea los recursos base de GameCloud en MiniStack: S3, CloudFront, DynamoDB y SQS.
# Ejecutar desde la raíz del repo: bash scripts/01_recursos_base.sh
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
AWSL="aws --endpoint-url=http://localhost:4566"

echo "== Inciso 1: frontend en S3 y CloudFront =="
$AWSL s3 mb s3://gamecloud-web
$AWSL s3 website s3://gamecloud-web --index-document index.html
$AWSL s3 cp web/index.html s3://gamecloud-web/index.html
$AWSL cloudfront create-distribution \
  --origin-domain-name gamecloud-web.s3.amazonaws.com \
  --default-root-object index.html > /dev/null

echo "== Inciso 2: tabla DynamoDB =="
$AWSL dynamodb create-table \
  --table-name Puntajes \
  --attribute-definitions AttributeName=juego,AttributeType=S AttributeName=jugador,AttributeType=S \
  --key-schema AttributeName=juego,KeyType=HASH AttributeName=jugador,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST > /dev/null

echo "== Inciso 3: colas SQS =="
$AWSL sqs create-queue --queue-name puntajes-dlq > /dev/null
DLQ_URL=$($AWSL sqs get-queue-url --queue-name puntajes-dlq --query "QueueUrl" --output text)
DLQ_ARN=$($AWSL sqs get-queue-attributes --queue-url $DLQ_URL --attribute-names QueueArn --query "Attributes.QueueArn" --output text)

cat > scripts/atributos-cola.json <<EOF
{
  "VisibilityTimeout": "30",
  "RedrivePolicy": "{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}"
}
EOF

$AWSL sqs create-queue --queue-name puntajes --attributes file://scripts/atributos-cola.json > /dev/null
echo "Listo."
