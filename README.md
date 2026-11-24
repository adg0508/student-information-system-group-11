# Student Information System Database
CMPE341, Group 11.

Run `docker compose up` from the project folder. Open http://localhost:5081.
Docker starts PostgreSQL and the Flask app. The first start loads the seven tables and sample records. The database volume keeps changes across restarts. Run `docker compose down` to stop.

| Username | Test password | Permissions |
| --- | --- | --- |
| admin | Group11-demo-admin | View, add, update and delete sample records |
| reader | Group11-demo-reader | View records |

These accounts are for the course demo. Only password hashes are used by the application.
The three report queries are in `queries.sql`.

## Hosted setup
For Supabase, open the SQL Editor in the project and run `database.sql` once in a database without the `sis` schema. Keep this schema private. In Railway, deploy the Dockerfile and set `DATABASE_URL` to the Supabase Session pooler connection string with SSL enabled. Set `SECRET_KEY` to a random private value to keep sessions valid across restarts. Generate a public HTTPS domain for the web service.
