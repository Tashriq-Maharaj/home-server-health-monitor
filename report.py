"""
Runs every registered check, catching errors per-check so one broken
service doesn't take down the whole report. Returns a list of sections
ready to hand to the HTML template.
"""
import logging
import checks  # noqa: F401  (imports register the checks via decorators)
from checks import CHECKS

log = logging.getLogger("server_report")


def run_all_checks():
    sections = []
    for name, fn in CHECKS:
        try:
            result = fn()
            result["name"] = name
        except Exception as e:
            log.exception("Check '%s' failed", name)
            result = {
                "name": name,
                "status": "down",
                "items": [("Error", str(e))],
            }
        sections.append(result)
    return sections
