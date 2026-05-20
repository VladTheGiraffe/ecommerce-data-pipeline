# E-Commerce Data Pipeline & API Scraper

## 📋 Business Problem
In high-volume e-commerce and sports card flipping, manual profitability tracking is inefficient and prone to human error. To scale inventory operations, businesses require automated systems to ingest marketplace data, calculate strict net return on investment (ROI) margins, and account for variable platform fees in real-time.

## 🛠️ Tech Stack & Infrastructure
- **Language:** Python 3.x
- **Libraries:** `requests` (API ingestion), `csv` (data parsing), `json`, `os`, `dotenv`
- **Infrastructure:** Headless local compute server (RTX 3060 Ti node), Windows/Linux environment
- **Data Sources:** Live eBay REST API payloads & bulk Active/Sold CSV reports

## 🏗️ System Architecture & Logic
1. **Environment Security:** Utilizes a decoupled `.env` architecture via `python-dotenv` to isolate local database and API credentials from the public repository.
2. **API Ingestion Layer:** Establishes HTTP connections to the live marketplace endpoints using the `requests` library, handling authentication headers and mapping dynamic JSON payloads directly into local memory structures.
3. **Data Pipeline & Parsing:** Parses bulk unstructured marketplace CSV reports dynamically via local Python routing functions to clean and structuralize transactional data.
4. **Core Margin Engine:** Executes an automated mathematical function to isolate exact micro-margins and net profitability on the fly using the strict operational formula:
   $$\text{Net ROI} = (\text{Sale Price} \times 0.86) - \text{Purchase Price}$$

## 🚀 How to Run Locally
1. Clone this repository.
2. Configure your local text `.env` file with your credentials:
   ```text
   DB_HOST=localhost
   DB_USER=postgres
   ...
