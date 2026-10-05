# Home Server Health Monitor

A lightweight Python monitoring application that checks the health and performance of a home server and generates a simple HTML health report.

The program monitors key system resources, Docker containers, and Prometheus, then provides a clear summary of the server's current state.

## Features

* **System Monitoring:** Check CPU, RAM, disk usage, and server uptime.
* **Docker Monitoring:** Check the status and uptime of running Docker containers.
* **Prometheus Monitoring:** Verify that the Prometheus monitoring service is healthy.
* **HTML Reports:** Generate a simple, readable server health report.
* **Email Reporting:** Send the health report through SMTP.
* **Environment Configuration:** Keep email and application configuration outside the source code.
* **Logging:** Record application activity and errors for troubleshooting.

## Example Report

The generated report provides a quick overview such as:

```text
🖥️ Home Server Health Report

🟢 Host Performance
CPU Usage: 2.94%
RAM Usage: 28.37%
Disk Usage: 39.67%
Uptime: 3.77 Days

🟢 Prometheus 👑
Prometheus: Healthy

🟢 Docker Containers 🐳
grafana: Up 28 hours
plex-exporter: Up 28 hours
prometheus: Up 28 hours
```

The report is designed to make it easy to see whether the server and its important services are operating normally.

## Technologies Used

* Python
* Prometheus
* Docker
* Docker SDK / Docker CLI integration
* SMTP
* HTML
* Jinja2
* python-dotenv
* Linux

## Requirements

* Python 3.10+
* Docker
* Prometheus
* SMTP email account
* Linux server recommended

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd Home-Server-Health-Monitor
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing the required configuration:

```env
PROM_URL=
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
EMAIL_TO=
```

Do not commit the `.env` file to GitHub.

## Running

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the program:

```bash
python3 main.py
```

The application will collect the configured server metrics, generate the health report, and send it through the configured SMTP server.

## Monitoring Approach

The application combines several sources of information to provide a single server health summary:

```text
Linux Server
     │
     ├── CPU / RAM / Disk / Uptime
     │
     ├── Docker
     │     └── Container Status
     │
     └── Prometheus
           └── Monitoring Health
                  │
                  ▼
             Python Monitor
                  │
                  ▼
             HTML Report
                  │
                  ▼
                Email
```

## Purpose

This project was created as part of my home lab to improve my understanding of Linux administration, Python automation, Docker monitoring, Prometheus, and automated reporting.

It also demonstrates how different infrastructure services can be combined into a small automation tool that provides useful operational information without requiring manual checks.

## Future Improvements

* Add alerting when resource usage exceeds configurable thresholds.
* Track service failures and recoveries.
* Add additional Prometheus metrics.
* Improve historical monitoring and reporting.
* Add automated tests.
* Run the monitoring process automatically using a systemd timer.

## License

Available for educational and personal use.
