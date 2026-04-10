# AWS Infrastructure Setup for CI/CD

Este documento contiene los comandos necesarios para configurar la infraestructura de AWS vía CLI.

## Variables de Configuración

```bash
# Set variables (personaliza estos valores)
export DOMAIN_NAME="data-platform"
export REPO_NAME="	data-platform-toolkit"
export AWS_REGION="us-west-2"
export GITHUB_ORG="joaquin-casanova"
export GITHUB_REPO="data-platform-toolkit"

# Get AWS Account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"
```

## Paso 1: Crear CodeArtifact Domain

```bash
# Create CodeArtifact domain
aws codeartifact create-domain \
  --domain "$DOMAIN_NAME" \
  --region "$AWS_REGION"

# Verify domain creation
aws codeartifact describe-domain \
  --domain "$DOMAIN_NAME" \
  --region "$AWS_REGION"
```

## Paso 2: Crear CodeArtifact Repository

```bash
# Create repository
aws codeartifact create-repository \
  --domain "$DOMAIN_NAME" \
  --repository "$REPO_NAME" \
  --region "$AWS_REGION" \
  --description "Python packages for data-platform-toolkit"

# Verify repository creation
aws codeartifact describe-repository \
  --domain "$DOMAIN_NAME" \
  --repository "$REPO_NAME" \
  --region "$AWS_REGION"
```

## Paso 3: Crear GitHub OIDC Provider

```bash
# Check if OIDC provider exists
aws iam list-open-id-connect-providers

# If not exists, create it
aws iam create-open-id-connect-provider \
  --url "https://token.actions.githubusercontent.com" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"

# Get the OIDC provider ARN
export OIDC_PROVIDER_ARN=$(aws iam list-open-id-connect-providers \
  --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')].Arn" \
  --output text)

echo "OIDC Provider ARN: $OIDC_PROVIDER_ARN"
```

## Paso 4: Crear IAM Policy

```bash
# Create policy document
cat > codeartifact-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "codeartifact:GetAuthorizationToken",
        "codeartifact:GetRepositoryEndpoint",
        "codeartifact:PublishPackageVersion",
        "codeartifact:PutPackageMetadata",
        "codeartifact:ReadFromRepository"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "sts:GetServiceBearerToken",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "sts:AWSServiceName": "codeartifact.amazonaws.com"
        }
      }
    }
  ]
}
EOF

# Create IAM policy
aws iam create-policy \
  --policy-name GitHubActionsCodeArtifactPolicy \
  --policy-document file://codeartifact-policy.json \
  --description "Policy for GitHub Actions to publish to CodeArtifact"

# Get policy ARN
export POLICY_ARN=$(aws iam list-policies \
  --query "Policies[?PolicyName=='GitHubActionsCodeArtifactPolicy'].Arn" \
  --output text)

echo "Policy ARN: $POLICY_ARN"
```

## Paso 5: Crear IAM Role con Trust Relationship

```bash
# Create trust policy document
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "$OIDC_PROVIDER_ARN"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:$GITHUB_ORG/$GITHUB_REPO:*"
        }
      }
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
  --role-name github-actions-codeartifact \
  --assume-role-policy-document file://trust-policy.json \
  --description "Role for GitHub Actions to publish to CodeArtifact"

# Attach policy to role
aws iam attach-role-policy \
  --role-name github-actions-codeartifact \
  --policy-arn "$POLICY_ARN"

# Get role ARN
export ROLE_ARN=$(aws iam get-role \
  --role-name github-actions-codeartifact \
  --query 'Role.Arn' \
  --output text)

echo "Role ARN: $ROLE_ARN"
```

## Paso 6: Resumen - Valores para GitHub Secrets

```bash
echo "=========================================="
echo "GitHub Secrets Configuration"
echo "=========================================="
echo "DATA_PLATFORM_TOOLKIT_AWS_ROLE: $ROLE_ARN"
echo "DATA_PLATFORM_TOOLKIT_AWS_ACCOUNT_ID: $AWS_ACCOUNT_ID"
echo "DATA_PLATFORM_TOOLKIT_CODEARTIFACT_DOMAIN: $DOMAIN_NAME"
echo "DATA_PLATFORM_TOOLKIT_CODEARTIFACT_REPO: $REPO_NAME"
echo "=========================================="
```

## Configurar GitHub Secrets

Ve a: https://github.com/joaquin-casanova/data-platform-toolkit/settings/secrets/actions

Agrega los 4 secrets con los valores impresos arriba.

## Cleanup (Opcional)

Si necesitas eliminar estos recursos:

```bash
# Detach policy from role
aws iam detach-role-policy \
  --role-name github-actions-codeartifact \
  --policy-arn "$POLICY_ARN"

# Delete role
aws iam delete-role --role-name github-actions-codeartifact

# Delete policy
aws iam delete-policy --policy-arn "$POLICY_ARN"

# Delete repository
aws codeartifact delete-repository \
  --domain "$DOMAIN_NAME" \
  --repository "$REPO_NAME" \
  --region "$AWS_REGION"

# Delete domain
aws codeartifact delete-domain \
  --domain "$DOMAIN_NAME" \
  --region "$AWS_REGION"
```

## Testing

### Verificar instalación desde CodeArtifact

```bash
# Get CodeArtifact repository URL
export CODEARTIFACT_URL=$(aws codeartifact get-repository-endpoint \
  --domain "$DOMAIN_NAME" \
  --repository "$REPO_NAME" \
  --format pypi \
  --query repositoryEndpoint \
  --output text)

# Get auth token
export CODEARTIFACT_TOKEN=$(aws codeartifact get-authorization-token \
  --domain "$DOMAIN_NAME" \
  --query authorizationToken \
  --output text)

# Install from CodeArtifact
pip install data-platform-toolkit \
  --index-url="https://aws:$CODEARTIFACT_TOKEN@${CODEARTIFACT_URL#https://}simple/"

# Verify installation
python -c "from data_platform_toolkit import __version__; print(__version__)"
```
