# DevTrack

DevTrack is a minimal Django backend API for tracking engineering bugs and tasks. Engineers can create reporters, create issues, retrieve records, and filter issues by status. The project follows the assignment requirement to keep the domain entities as ordinary Python classes and persist records in JSON files rather than using Django ORM models.

## Features

The API supports reporter creation and lookup, issue creation and lookup, status filtering, input validation, and priority-specific polymorphism. Critical issues return an urgent description, low-priority issues return a lower-urgency description, and medium/high-priority issues use the base `Issue.describe()` implementation.

## Project structure

```text
devtrack/
├── manage.py
├── requirements.txt
├── issues.json
├── reporters.json
├── README.md
├── docs/
│   ├── manual_test_results.md
│   └── postman/
├── devtrack/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── issues/
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
└── tests/
    ├── test_api.py
    └── test_models.py
```

## Setup and execution

Use Python 3.10 or newer. From the project directory, create and activate a virtual environment, install the dependencies, run the checks, and start the development server.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py check
python manage.py test tests
python manage.py runserver
```

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1` instead of the `source` command. The API is then available at `http://127.0.0.1:8000`.

## Data storage

The project stores reporters in `reporters.json` and issues in `issues.json` at the repository root. The view layer contains small JSON read/write helpers so that the persistence behavior is explicit and easy to inspect. IDs are generated from the highest existing integer ID when a POST request does not provide one.

## OOP design

`BaseEntity` is an abstract base class with an abstract `validate()` method and a reusable `to_dict()` method. `Reporter` validates the name and email. `Issue` validates the title, status, and priority. `CriticalIssue` and `LowPriorityIssue` inherit from `Issue` and override `describe()` to demonstrate method overriding and polymorphism.

The POST issue view chooses the class from the submitted priority, calls `validate()`, serializes the object with `to_dict()`, and adds the result of `describe()` as the response `message`.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/reporters/` | Create a reporter. |
| `GET` | `/api/reporters/` | Return all reporters. |
| `GET` | `/api/reporters/?id=1` | Return one reporter by integer ID. |
| `POST` | `/api/issues/` | Create an issue and return its priority-specific message. |
| `GET` | `/api/issues/` | Return all issues. |
| `GET` | `/api/issues/?id=1` | Return one issue by integer ID. |
| `GET` | `/api/issues/?status=open` | Return issues matching a valid status. |

The accepted issue statuses are `open`, `in_progress`, `resolved`, and `closed`. The accepted priorities are `low`, `medium`, `high`, and `critical`.

### Create a reporter

```http
POST /api/reporters/
Content-Type: application/json
```

```json
{
  "id": 1,
  "name": "Asha Rao",
  "email": "asha@example.com",
  "team": "backend"
}
```

A successful request returns `201 Created` and the saved reporter object. The `id` field may be omitted to generate the next available integer ID.

### Create a critical issue

```http
POST /api/issues/
Content-Type: application/json
```

```json
{
  "id": 1,
  "title": "Login button not working on mobile",
  "description": "Users on iOS 17 cannot tap the login button",
  "status": "open",
  "priority": "critical",
  "reporter_id": 1
}
```

The response has status `201 Created` and includes the following message:

```text
[URGENT] Login button not working on mobile — needs immediate attention
```

### Validation and not-found responses

Invalid input returns `400 Bad Request`. For example, an empty issue title returns:

```json
{
  "error": "Title cannot be empty"
}
```

A lookup for a missing issue returns `404 Not Found`:

```json
{
  "error": "Issue not found"
}
```

## Testing

Run the automated suite with:

```bash
python manage.py test tests
```

The suite covers the entity validation rules, serialization, subclass behavior, reporter creation and lookup, issue creation, filtering, validation failures, and 404 responses. A record of the live API checks is available in [`docs/manual_test_results.md`](docs/manual_test_results.md).

The repository also includes live API response evidence: [success response](docs/postman/success_get_open_issues.png) and [failure response](docs/postman/failure_missing_issue.png). For the assignment's strict Postman evidence requirement, import [`DevTrack.postman_collection.json`](docs/postman/DevTrack.postman_collection.json) into Postman, run one successful request and one failure request, and replace or supplement these images with screenshots that show the Postman request and response panels before submitting the repository.

## Design decision

The assignment explicitly requests JSON-file storage, so this project does not create Django database models. Keeping persistence in two JSON files makes the data flow visible and keeps the OOP classes focused on validation and behavior. The trade-off is that this storage approach is intended for a learning project rather than concurrent production traffic.

## References

[1]: https://docs.djangoproject.com/en/5.2/ "Django documentation"

[2]: https://docs.python.org/3/library/abc.html "Python abstract base classes documentation"
