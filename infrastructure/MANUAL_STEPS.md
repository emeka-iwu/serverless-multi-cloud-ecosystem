# Manual Infrastructure Setup Guide

This document outlines the manual configuration steps taken in the AWS Console to build a serverless ecosystem integrated with Google and Zoho.

---

## 1. Networking & DNS (Multi-Cloud Orchestration)
* **Domain Registrar:** Namecheap.
* **DNS Strategy:**
    * **Apex Domain (@):** Points to **AWS CloudFront** via ALIAS record.
    * **Subdomain (www):** Points to **Google Sites** via CNAME for the primary bio website.
    * **Email (Zoho):** Managed via MX and SPF/DKIM TXT records on Namecheap.

## 2. Storage & Frontend: Amazon S3
* **Bucket Name:** `p2p-fifa-waitlist-static-website-2024`
* **Static Website Hosting:** Enabled.
* **Public Access:** **ON** (Block All Public Access disabled; `PublicReadGetObject` policy applied).
* **Integration:** The HTML form in this bucket is configured to `POST` data to the **API Gateway** endpoint.

## 3. Entry Point: Amazon CloudFront
* **SSL/TLS:** Managed via AWS Certificate Manager (ACM) for `emeka.cloud`.
* **Edge Logic (CloudFront Functions):**
    * **Apex Redirect:** Redirects `emeka.cloud/` (root) to `www.emeka.cloud` (Google Sites).
    * **Path Preservation:** Serves the S3 waitlist content for the `/waitlist` path.

## 4. API Layer: Amazon API Gateway (HTTP API)
* **Endpoint:** `/signups`
* **Method:** `POST`
* **CORS Configuration:** Allowed origins configured to `https://emeka.cloud` to prevent unauthorized cross-site submissions.
* **Integration:** Triggers the Backend Lambda function upon receiving a valid request.

## 5. Security: IAM Role & Policies
The Lambda function uses a custom execution role with permissions scoped to the minimum necessary actions (Least Privilege):
* **Logging:** CloudWatch Logs enabled for execution tracing and debugging.
* **Secrets:** `GetSecretValue` restricted specifically to the Aurora Postgres credentials in Secrets Manager.
* **RDS Data:** Access to `ExecuteStatement` and transaction actions for the Aurora Postgres cluster.
* **SES:** Permission to `SendEmail` and `SendRawEmail` for automated waitlist confirmations.

## 6. Compute & Messaging: Lambda & SES
* **Lambda Function:** Processes incoming JSON, authenticates with RDS via Secrets Manager, and writes to Postgres.
* **Amazon SES (Production Mode):** * **Status:** Successfully moved from Sandbox to **Production**.
    * **Function:** Sends a confirmation email to any user who successfully joins the waitlist.
    * **Verification:** Domain identity verified via DKIM in Namecheap.

## 7. Database: Amazon Aurora Serverless v2
* **Engine:** **PostgreSQL** (Data API enabled).
* **Capacity:** * **Min ACU:** 0 (Scale-to-zero enabled for $0/month base cost).
    * **Max ACU:** 1.0 (Safety ceiling).
* **Important Note on Latency:** Because the DB scales to 0 ACU, it enters a "sleep" state. The first user request may trigger a **"Cold Start" (5-10s delay)**. Users may need to resubmit the form if the initial connection times out while the DB wakes up. This is an intentional trade-off to prioritize cost-efficiency.

---

## ⚠️ Architectural Decision: The Cost-First Model
Every component in this stack was chosen to provide a professional, scalable user experience while maintaining a near-zero cost footprint during the development phase. By leveraging scale-to-zero technology (Aurora) and serverless execution (Lambda/API Gateway), the infrastructure remains highly efficient.
