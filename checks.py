"""
Each check is a small, independent function registered with @check(...).
It must return a dict:
    {
        "status": "ok" | "warn" | "down",
        "items": [ ("label", "value"), ... ]
    }

If a check raises, the report shows it as failed instead of crashing the
whole run -- see report.run_all_checks().

To add a new monitored service later: write a function, decorate it with
@check("Some Section Name"), return items. Nothing else needs to change.
"""
import logging
import subprocess
import requests
import pyodbc

from config import Config

log = logging.getLogger("server_report")

CHECKS = []  # list of (section_name, function)


def check(section_name: str):
    def decorator(fn):
        CHECKS.append((section_name, fn))
        return fn
    return decorator


def _query_prom(query: str, timeout: int = 5):
    r = requests.get(f"{Config.PROM_URL}/api/v1/query", params={"query": query}, timeout=timeout)
    r.raise_for_status()
    result = r.json()["data"]["result"]
    if not result:
        return None
    return round(float(result[0]["value"][1]), 2)


@check("Host Performance")
def host_performance():
    cpu = _query_prom('100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)')
    ram = _query_prom('(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100')
    disk = _query_prom('100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"})')
    uptime = _query_prom('sum(node_time_seconds - node_boot_time_seconds) / 86400')

    return {
        "status": "ok",
        "items": [
            ("CPU Usage", f"{cpu}%" if cpu is not None else "N/A"),
            ("RAM Usage", f"{ram}%" if ram is not None else "N/A"),
            ("Disk Usage", f"{disk}%" if disk is not None else "N/A"),
            ("Uptime", f"{uptime} Days" if uptime is not None else "N/A"),
        ],
    }


@check("Prometheus 👑")
def prometheus_status():
    up = _query_prom("up")
    healthy = up is not None
    return {
        "status": "ok" if healthy else "down",
        "items": [("Prometheus", "Healthy" if healthy else "Unreachable")],
    }


@check("Docker Containers 🐳")
def docker_status():
    raw = subprocess.check_output(
        ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}"],
        timeout=10,
    ).decode("utf-8").strip()

    items = []
    all_up = True
    for line in raw.split("\n"):
        if not line:
            continue
        name, status = line.split("|", 1)
        up = "Up" in status
        all_up = all_up and up
        items.append((name, status))

    return {"status": "ok" if all_up else "warn", "items": items}





@check("️MS SQL Server 🗄️")
def sql_status():
    conn = pyodbc.connect(Config.MSSQL_CONN_STR, timeout=5)
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE state_desc = 'ONLINE'")
        db_count = cursor.fetchone()[0]

        cursor.execute(
            "SELECT cntr_value FROM sys.dm_os_performance_counters "
            "WHERE counter_name = 'Buffer cache hit ratio'"
        )
        
        
        row = cursor.fetchone()
        cache_hit = row[0] if row else "N/A"

        return {
            "status": "ok",
            "items": [
                ("Online Databases", db_count),
                ("Buffer Cache Hit Ratio", f"{cache_hit}%"),
            ],
        }
    finally:
        conn.close()



@check("Plex 📺")
def plex_status():
    plex_up = _query_prom("plex_up")

    if plex_up is None:
        return {
            "status": "down",
            "items": [("Plex Server", "No data from exporter")],
        }

    if plex_up < 1:
        return {
            "status": "down",
            "items": [("Plex Server", "Down / Unreachable")],
        }

    # Query specific media types using Prometheus label filters
    movies_count = _query_prom('plex_media_count{type="movie"}')
    shows_count = _query_prom('plex_media_count{type="show"}')
    episodes_count = _query_prom('plex_media_count{type="show_episode"}')

    sessions = _query_prom("plex_sessions_count")
    video_transcodes = _query_prom("plex_video_transcode_sessions_count")
    audio_transcodes = _query_prom("plex_audio_transcode_sessions_count")

    return {
        "status": "ok",
        "items": [
            ("Plex Server", "Healthy"),
            ("Movies", int(movies_count) if movies_count is not None else "N/A"),
            ("TV Shows", int(shows_count) if shows_count is not None else "N/A"),
            ("Episodes", int(episodes_count) if episodes_count is not None else "N/A"),
            ("Active Sessions", int(sessions) if sessions is not None else "N/A"),
            (
                "Video Transcodes",
                int(video_transcodes) if video_transcodes is not None else "N/A",
            ),
            (
                "Audio Transcodes",
                int(audio_transcodes) if audio_transcodes is not None else "N/A",
            ),
        ],
    }

# ---- Add future checks below, e.g.: ----





@check("System Service Failures️")
def failed_services():
    raw = subprocess.check_output(
        ["systemctl", "--failed", "--no-legend"], timeout=10
    ).decode("utf-8").strip()

    if not raw:
        return {"status": "ok", "items": [("Failed units", "None")]}

    items = [(line.strip(), "failed") for line in raw.split("\n") if line]
    return {"status": "warn", "items": items}


