# Manual API Test Results

The following checks were run against the local Django server at `http://127.0.0.1:8000`.

| Request | Expected result | Observed result |
|---|---:|---:|
| `POST /api/reporters/` with a valid reporter | `201 Created` | `201 Created` |
| `POST /api/issues/` with `priority=critical` | `201 Created` and urgent message | `201 Created`; response included `[URGENT] Login button not working on mobile — needs immediate attention` |
| `GET /api/issues/?status=open` | `200 OK` with matching issues | `200 OK`; returned the created open issue |
| `POST /api/issues/` with an empty title | `400 Bad Request` | `400 Bad Request`; returned `{"error": "Title cannot be empty"}` |
| `GET /api/issues/?id=999` | `404 Not Found` | `404 Not Found`; returned `{"error": "Issue not found"}` |

These checks demonstrate both a successful request and a failure request, as required by the assignment. The JSON data files contain the valid sample reporter and issue created during the live test.
