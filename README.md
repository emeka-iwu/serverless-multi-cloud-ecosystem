# Serverless Multi-Cloud Waitlist Ecosystem 

A high-availability, cost-optimized serverless architecture bridging **AWS**, **Google Cloud**, and **Zoho** to manage an elite gaming waitlist.



## 🌐 The Architecture
This project demonstrates a sophisticated multi-cloud routing strategy:
* **Edge Routing:** AWS CloudFront acts as a global traffic controller. Using **CloudFront Functions**, the apex domain (`emeka.cloud`) is routed to a **Google Sites** bio page, while the `/waitlist` path is routed to an **AWS S3** static site.
* **Backend:** A high-performance **Amazon API Gateway (HTTP API)** triggers a Python-based **AWS Lambda** function.
* **Database:** **Amazon Aurora Serverless v2 (PostgreSQL)** utilizing the Data API for secure, connectionless HTTPS queries.
* **Communications:** **Amazon SES (Production Mode)** with custom MAIL FROM domain identity for automated user onboarding.

## ⚙️ Technical Data Flow
1. **Request:** User submits a form at `emeka.cloud/waitlist`.
2. **Gateway:** The browser sends a `POST` request to the **API Gateway HTTP endpoint**.
3. **Compute:** Lambda parses the JSON, retrieves DB credentials from **Secrets Manager**, and executes a parameterized SQL insert into **Aurora Postgres**.
4. **Messaging:** Upon successful DB write, Lambda triggers **SES** to send a branded confirmation email to the user.
5. **Response:** A 200 OK status with custom **CORS headers** is returned to the frontend.

## 🛠️ Tech Stack
| Layer | Technology |
| :--- | :--- |
| **DNS / Mail** | Namecheap, Zoho EU |
| **Frontend** | HTML5, CSS3, JavaScript (S3 + CloudFront) |
| **Compute** | AWS Lambda (Python 3.12) |
| **API** | Amazon API Gateway (HTTP API) |
| **Database** | Amazon Aurora Serverless v2 (PostgreSQL) |
| **Security** | AWS IAM (Least Privilege), AWS Secrets Manager, ACM (SSL/TLS) |

## ✨ Key Features & Engineering Decisions

### 💰 Zero-Base Cost Optimization
The infrastructure utilizes **Aurora Serverless v2 with 0 ACU scaling**. The database automatically pauses during inactivity, reducing compute costs to $0.00/month. *Note: This introduces a 5-10s "cold start" latency, an intentional trade-off for MVP cost-efficiency.*

### 🔐 Security & Least Privilege
* **Environment Isolation:** Sensitive ARNs are managed via **Lambda Environment Variables**; no credentials exist in the source code.
* **Strict CORS:** The HTTP API is hardened to only accept traffic from `https://emeka.cloud`.
* **IAM Scoping:** The Lambda role is restricted to `rds-data` and `ses:SendEmail` for specific resource ARNs only.

### 📧 Production-Grade Email
Unlike many sandbox projects, this ecosystem uses a **Verified SES Production Identity**. It features a custom `MAIL FROM` domain (`mail.emeka.cloud`) with SPF and DKIM records configured to ensure DMARC alignment and high deliverability.

## 📂 Repository Structure
* `frontend/`: Static web assets and client-side logic.
* `backend/lambda-functions/`: Python logic for database processing and email triggers.
* `infrastructure/`: 
    * `iam-policies/`: JSON definitions for security roles.
    * `cloudfront/`: Edge logic for domain redirection.
    * `MANUAL_STEPS.md`: Comprehensive guide of the AWS Console configuration.

## 🚀 How to Deploy
Detailed manual configuration steps can be found in the [Infrastructure Manual](./infrastructure/MANUAL_STEPS.md).
