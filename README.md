# AI-Assisted Design Validation and Performance Analysis

## Overview

This project demonstrates a **production-style validation and performance analysis framework** inspired by real-world hardware and system-level design workflows.

The system automates the process of:

* running an **emulated system environment**
* collecting **large volumes of performance logs**
* parsing raw logs into structured metrics
* analyzing design and performance behavior
* identifying **bottlenecks and anomalies** using data-driven techniques and machine learning

The project represents foundational work toward **AI-assisted CAD, validation, and sign-off workflows**, where automation and ML reduce manual analysis time and improve validation throughput.

---

## What problem does this solve?

In real hardware and system design flows:

* Emulators and simulators generate **massive log files**
* Engineers manually inspect latency, cache behavior, IPC, and error trends
* Bottleneck identification and regression analysis are time-consuming
* Validation throughput is limited by manual triage

This project automates that pipeline and adds **AI-assisted analysis** to:

* accelerate validation
* consistently detect performance issues
* reduce manual effort

---

## High-Level System Architecture

```
Emulated System
   ↓ (performance logs)
Log Collection (subprocess)
   ↓
Log Parsing (structured metrics)
   ↓
Storage (SQLite)
   ↓
KPI Analysis + Bottleneck Rules
   ↓
ML Anomaly Detection
   ↓
FastAPI Reports
```

---

## Key Features

* **Emulated system environment**

  * Simulates an emulator producing realistic performance logs
* **Python-based automation**

  * Launches and controls validation runs programmatically
* **Large-scale data collection**

  * Streams and stores many samples per run
* **Log parsing**

  * Converts raw logs into structured numerical metrics
* **Performance analysis**

  * Computes KPIs such as latency (mean / p95), cache miss rate, IPC, and error rate
* **Bottleneck detection**

  * Rule-based engineering heuristics
* **AI-assisted analysis**

  * Isolation Forest–based anomaly detection
* **FastAPI service**

  * Exposes validation workflows via REST APIs
* **Reproducible & portfolio-safe**

  * No proprietary tools required

---

## What is the “emulated system” here?

In industry, validation engineers treat simulators and emulators as **black boxes** that output logs.

This project uses a **mock emulator** that:

* streams realistic metrics (latency, cache misses, IPC, errors)
* supports different behavioral profiles:

  * `baseline`
  * `cache_stress`
  * `timing_bug`

This preserves the **workflow and tooling logic** without requiring proprietary EDA tools.

---

## API Endpoints Explained

### Health Check

`GET /v1/health`

**Purpose:**
Confirms that the service is running and configuration is loaded.

**Example Response:**

```json
{
  "status": "ok",
  "db_path": "./runs.db",
  "emu_default_duration_sec": 15,
  "emu_default_hz": 15
}
```

This endpoint is used for:

* monitoring
* debugging
* validation of system readiness

---

### Start a Validation Run

`POST /v1/runs`

**Purpose:**
Launches a validation run against an emulated environment.

**Request Body Example:**

```json
{
  "profile": "cache_stress",
  "duration_sec": 10,
  "hz": 20
}
```

**Profiles:**

* `baseline` – normal behavior
* `cache_stress` – elevated cache misses and latency
* `timing_bug` – higher tail latency and error probability

**Response Example:**

```json
{
  "run_id": "a1b2c3...",
  "created_at": "2026-01-09T12:00:00Z",
  "profile": "cache_stress",
  "samples": 200,
  "parse_failures": 0
}
```

---

### List Runs

`GET /v1/runs`

Returns all stored validation runs with metadata.

---

### Analysis Report

`GET /v1/runs/{run_id}/report`

**Purpose:**
Analyzes a completed run and returns:

* aggregated KPIs
* detected bottlenecks
* ML anomaly signal

**Example Response:**

```json
{
  "run_id": "a1b2c3...",
  "kpis": {
    "samples": 200,
    "latency_mean_ms": 28.4,
    "latency_p95_ms": 46.8,
    "ipc_mean": 1.15,
    "cache_miss_mean": 0.14,
    "error_rate": 0.03,
    "warning_rate": 0.07
  },
  "bottlenecks": [
    "High tail latency (p95=46.80ms) → potential timing / critical-path bottleneck.",
    "Elevated cache miss rate (mean=0.140) → potential memory locality / cache configuration issue."
  ],
  "ml": {
    "anomaly_score": -0.21,
    "is_anomalous": 1
  }
}
```

---

## How Bottlenecks Are Identified

### Rule-based Analysis

* High p95 latency → timing / critical-path issues
* High cache miss rate → memory locality or cache configuration problems
* Elevated error rate → functional or timing violations

### ML-based Analysis

* Isolation Forest detects anomalous runs using:

  * latency p95
  * cache miss mean
  * error rate

This demonstrates **AI-assisted validation triage**.

---

## How to Run the Project (Step-by-Step)

### Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create environment config

```bash
copy .env.example .env
```

### Start the API

```bash
python -m uvicorn app.main:app --reload
```

You should see:

```
Startup complete.
```

---

## How to Verify It Works

### Option 1: Swagger UI (Recommended)

Open:

```
http://127.0.0.1:8000/docs
```

**Step-by-step check:**

1. Run `GET /v1/health`
2. Run `POST /v1/runs` (choose a profile)
3. Copy the returned `run_id`
4. Call `GET /v1/runs/{run_id}/report`
5. Confirm KPIs, bottlenecks, and ML output appear

---

### Option 2: Batch Demo (Terminal)

With the API running:

```bash
python scripts/run_batch.py
```

This executes multiple validation profiles and prints analysis results.

---

## Why This Project Is Relevant

This project reflects **real validation and CAD tooling workflows**, including:

* emulator log consumption
* performance characterization
* regression detection
* AI-assisted triage

It intentionally focuses on the **automation and analysis layer**, not RTL implementation, which is where AI can provide the highest leverage in modern design flows.

---

