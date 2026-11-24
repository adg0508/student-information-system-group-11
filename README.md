# Student Information System Database
CMPE341, Group 11.

Open the [live application](https://web-production-8249f41a.up.railway.app).

Run `docker compose up` from the project folder. Open http://localhost:5081.
Docker starts PostgreSQL and the Flask app. The first start loads the seven tables and sample records. The database volume keeps changes across restarts. Run `docker compose down` to stop.

| Username | Test password | Permissions |
| --- | --- | --- |
| admin | Group11-demo-admin | View, add, update and delete sample records |
| reader | Group11-demo-reader | View records |

These accounts are for the course demo. Only password hashes are used by the application.
The three report queries are in `queries.sql`.

## Hosted setup
Railway runs the Dockerfile. Supabase stores the course records in PostgreSQL. The container checks that the seven project tables are ready before starting the web app. For a new hosted setup, run database.sql once as the database owner. Set DATABASE_URL in Railway to the SSL session pooler connection for an application account with access to the sis tables and sequences. Set SECRET_KEY to a random private value and generate a public domain for the web service.
