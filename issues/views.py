import json
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CriticalIssue, Issue, LowPriorityIssue, Reporter


REPORTERS_FILE = Path(settings.BASE_DIR) / "reporters.json"
ISSUES_FILE = Path(settings.BASE_DIR) / "issues.json"


def _read_records(file_path):
    """Read a JSON list from disk, treating a missing file as an empty list."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError:
        return []

    return records if isinstance(records, list) else []


def _write_records(file_path, records):
    """Persist records as readable, indented JSON."""
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
        file.write("\n")


def _parse_json_body(request):
    """Return a JSON object or a JSON error response."""
    try:
        raw_body = request.body.decode("utf-8")
        data = json.loads(raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, JsonResponse({"error": "Invalid JSON"}, status=400)

    if not isinstance(data, dict):
        return None, JsonResponse(
            {"error": "Request body must be a JSON object"},
            status=400,
        )
    return data, None


def _next_id(records):
    """Generate the next integer ID without relying on a database."""
    numeric_ids = [
        int(record["id"])
        for record in records
        if str(record.get("id", "")).isdigit()
    ]
    return max(numeric_ids, default=0) + 1


def _coerce_integer(value, field_name):
    """Convert a value to int or raise a user-facing validation error."""
    if value is None or value == "":
        raise ValueError(f"{field_name} is required")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _find_by_id(records, record_id):
    return next(
        (record for record in records if record.get("id") == record_id),
        None,
    )


def _method_not_allowed():
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def reporters(request):
    """Create reporters or retrieve all reporters/a reporter by ID."""
    records = _read_records(REPORTERS_FILE)

    if request.method == "POST":
        data, error_response = _parse_json_body(request)
        if error_response:
            return error_response

        try:
            reporter_id = _coerce_integer(
                data.get("id", _next_id(records)),
                "ID",
            )
            reporter = Reporter(
                id=reporter_id,
                name=data.get("name"),
                email=data.get("email"),
                team=data.get("team", ""),
            )
            reporter.validate()
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        if _find_by_id(records, reporter_id):
            return JsonResponse(
                {"error": "Reporter with this ID already exists"},
                status=400,
            )

        reporter_data = reporter.to_dict()
        records.append(reporter_data)
        _write_records(REPORTERS_FILE, records)
        return JsonResponse(reporter_data, status=201)

    if request.method != "GET":
        return _method_not_allowed()

    reporter_id_param = request.GET.get("id")
    if reporter_id_param is None:
        return JsonResponse(records, safe=False, status=200)

    try:
        reporter_id = _coerce_integer(reporter_id_param, "ID")
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    reporter = _find_by_id(records, reporter_id)
    if reporter is None:
        return JsonResponse({"error": "Reporter not found"}, status=404)
    return JsonResponse(reporter, status=200)


@csrf_exempt
def issues(request):
    """Create issues or retrieve issues by ID, status, or collection."""
    records = _read_records(ISSUES_FILE)

    if request.method == "POST":
        data, error_response = _parse_json_body(request)
        if error_response:
            return error_response

        try:
            issue_id = _coerce_integer(
                data.get("id", _next_id(records)),
                "ID",
            )
            reporter_id = _coerce_integer(data.get("reporter_id"), "reporter_id")
            priority = data.get("priority")
            issue_kwargs = {
                "id": issue_id,
                "title": data.get("title"),
                "description": data.get("description", ""),
                "status": data.get("status"),
                "priority": priority,
                "reporter_id": reporter_id,
            }
            if "created_at" in data:
                issue_kwargs["created_at"] = data["created_at"]

            if priority == "critical":
                issue = CriticalIssue(**issue_kwargs)
            elif priority == "low":
                issue = LowPriorityIssue(**issue_kwargs)
            else:
                issue = Issue(**issue_kwargs)
            issue.validate()
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        if _find_by_id(records, issue_id):
            return JsonResponse(
                {"error": "Issue with this ID already exists"},
                status=400,
            )

        issue_data = issue.to_dict()
        issue_data["message"] = issue.describe()
        records.append(issue_data)
        _write_records(ISSUES_FILE, records)
        return JsonResponse(issue_data, status=201)

    if request.method != "GET":
        return _method_not_allowed()

    issue_id_param = request.GET.get("id")
    if issue_id_param is not None:
        try:
            issue_id = _coerce_integer(issue_id_param, "ID")
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        issue = _find_by_id(records, issue_id)
        if issue is None:
            return JsonResponse({"error": "Issue not found"}, status=404)
        return JsonResponse(issue, status=200)

    status_filter = request.GET.get("status")
    if status_filter is not None:
        if status_filter not in Issue.ALLOWED_STATUSES:
            allowed = ", ".join(sorted(Issue.ALLOWED_STATUSES))
            return JsonResponse(
                {"error": f"Status must be one of: {allowed}"},
                status=400,
            )
        records = [record for record in records if record.get("status") == status_filter]

    return JsonResponse(records, safe=False, status=200)
