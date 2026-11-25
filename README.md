# Student Information System Database

CMPE341, Group 11

[Open the Student Information System](https://web-production-8249f41a.up.railway.app) and sign in with one of the accounts below. Use the admin account to try the forms shown in the report.

| Username | Password | What you can do |
| --- | --- | --- |
| `admin` | `Group11-demo-admin` | View, add, edit and delete records |
| `reader` | `Group11-demo-reader` | View records in all seven tables |

## Run the project locally

After cloning the repository, open the project folder and run:

```sh
docker compose up
```

Open [localhost:5081](http://localhost:5081) and use the same accounts. On the first run, Docker creates the PostgreSQL tables and loads the sample records from `database.sql`. Run `docker compose down` to stop the app. Your changes are saved in the database volume.

The live site runs on Railway and uses a Supabase PostgreSQL database. The three queries from the report are in [queries.sql](queries.sql).
