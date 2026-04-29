# GROC v2.0 Backend Engine(The API Edition) 🚀

### *The Evolution of GROC: A Professional API Refactor*

## 📜 Project Context
This repository contains the core REST API for the **GROC v2.0 Marketplace**. It is a specialized, backend-only evolution of my CS50P capstone project (**GROC**). 

The primary goal of this refactor was to move away from local file-based storage (CSV) and implement industry-standard security and relational data management. 

## 🛠️ Key Improvements Over v1.0 (GROC)

### 1. High-Performance Data Layer (PostgreSQL)
Unlike the original CSV-based system which required reading the entire file for every transaction, this version utilizes **PostgreSQL**.
* **Filtering & Searching:** Leverages SQL indexing for near-instant retrieval of products and users.
* **Scalability:** Designed to handle thousands of records without the data-loss risks associated with manual CSV rewriting.

### 2. Hardened Security & Identity
* **Bcrypt Hashing:** User passwords are no longer stored in plaintext. Utilizing `passlib` ensures that even in a database breach, user credentials remain secure.
* **JWT Authentication:** Implemented JSON Web Tokens (JWT) for secure, stateless communication. 
* **Role-Based Access Control (RBAC):** Integrated logic to distinguish between Buyers and Sellers, ensuring write-access to the inventory is strictly restricted.

### 3. Production Readiness
* **Cloud Compatible:** The architecture is decoupled and configured via environment variables (`.env`), making it ready for deployment to platforms like AWS, Heroku, or DigitalOcean.
* **Relational Integrity:** Uses Foreign Key constraints to maintain a perfect link between Sellers, Products, and Orders.

Got it! You want the clean, bulleted look using actual Markdown symbols (like * or -) rather than just emojis. This makes the text look very crisp and technical on GitHub.

Here is that section styled with clean Markdown symbols and bold headers:

⚠️ Current Development & Learning Roadmap
This project is a functional learning milestone. I am currently focusing on mastering the fundamentals of REST APIs and Relational Databases. Because this is an evolving build, there are specific limitations I am addressing in future updates:

[Concurrency] — This version currently uses Synchronous logic. As I progress in my studies of non-blocking I/O, I plan to implement async/await to handle high-concurrency requests and optimize performance.

[Token Lifecycle] — While JWT Authentication is fully implemented for secure authorization, advanced state management—specifically Refresh Tokens—is slated for the next development cycle to improve the user session experience.

[Role-Based Enforcement] — The is_seller data structure is established; the next step is implementing middleware to strictly gatekeep seller-only endpoints.

## 📂 Backend-Only Architecture
This repository is **Frontend-Agnostic**. It provides the raw API endpoints intended to serve as the "Engine" for Web, Mobile, or Desktop client applications.

### Technical Documentation
Once the server is running locally, the full Interactive API Documentation is available via FastAPI's built-in Swagger UI at:
`http://127.0.0.1:8000/docs`

---
*Developed by Faizan Luthyanvi | LogicNomad*