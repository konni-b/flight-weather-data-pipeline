# ✈️ Flight & Weather Data Pipeline: The 2022 Holiday Meltdown

An end-to-end analytics engineering pipeline (GCP, dbt, BigQuery) analyzing the impact of extreme winter weather on US flight performance, with a specific focus on the Southwest Airlines scheduling collapse.

---

## 🌪️ The Context: Winter Storm Elliott

Between December 21 and 26, 2022, a historic extratropical cyclone — unofficially named Winter Storm Elliott — brought blizzard conditions and dangerously low temperatures to a massive portion of the United States and Canada. 

The storm hit during one of the busiest travel weeks of the year, immediately disrupting the US aviation network.

**The "Data" Problem:** <br>
While most major airlines recovered as the weather cleared, **Southwest Airlines** experienced a catastrophic operational collapse. Their outdated, point-to-point routing model and legacy crew-scheduling software could not handle the sheer volume of rerouting required. The system failed, leaving crews stranded and resulting in the cancellation of over 15,000 flights.

## 🎯 Project Objective

The goal of this project is to build an **Analytics Engineering pipeline** to ingest, process, and model the raw data from this event. By joining Bureau of Transportation Statistics (BTS) flight data with historical weather APIs, this pipeline answers key questions:

* How did the initial weather event cascade into a systemic failure for specific airlines?
* Can we visualize the exact timeline of when Southwest's recovery diverged from its competitors (like Delta or United)?
* What is the statistical correlation between specific weather metrics (snowfall, freezing temperatures) and carrier-specific cancellation codes?

## 🏗️ Architecture & Tech Stack

This project implements an ELT (Extract, Load, Transform) architecture using the following industry-standard tools:

* **Infrastructure as Code (IaC):** Terraform
* **Environment Management:** `uv` (Python 3.12)
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Data Lake:** Google Cloud Storage (GCS)
* **Data Warehouse:** BigQuery
* **Transformation:** dbt (Data Build Tool)
* **Orchestration:** Kestra *(Upcoming)*


## Sources

* **Wikipedia:** [2022 Southwest Airlines scheduling crisis](https://en.wikipedia.org/wiki/2022_Southwest_Airlines_scheduling_crisis)
