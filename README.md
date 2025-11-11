# Serverless URL Shortener - AWS

A production-ready serverless URL shortener built with AWS Lambda, API Gateway, and DynamoDB. Demonstrates full-stack serverless architecture with cost-effective scaling.

## 🏗️ Architecture

```mermaid
graph TB
    A[User] --> B[Frontend - S3]
    B --> C[API Gateway]
    C --> D[Create Lambda]
    C --> E[Redirect Lambda]
    D --> F[DynamoDB]
    E --> F
    E --> G[302 Redirect]
    
    style A fill:#ff6b6b
    style B fill:#4ecdc4
    style C fill:#45b7d1
    style D fill:#96ceb4
    style E fill:#96ceb4
    style F fill:#feca57
```

