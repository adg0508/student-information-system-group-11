# Student Information System Database

We are Group 11. For our CMPE341 project, we built a database for students, courses and grades. A student can take several courses, so we keep a separate enrollment record for each course section they take. We used Supabase for the database and Railway for the website.

[Open the website](https://web-production-8249f41a.up.railway.app) and sign in with one of our test accounts. To see the Students page shown in our report, use the admin account.

| Username | Password | What you can do |
| --- | --- | --- |
| `admin` | `Group11-demo-admin` | View, add, edit and delete records |
| `reader` | `Group11-demo-reader` | View records in all seven tables |

## Run it on your computer

Clone the repository. Open a terminal in the project folder and run this command.

```sh
docker compose up
```

Then open [localhost:5081](http://localhost:5081) and sign in with the same accounts. The first time you run the project, Docker creates the tables and adds the sample data from `database.sql`. You can stop the app with `docker compose down`. Your records will still be there the next time you start it.

We used the three queries in [queries.sql](queries.sql) for the results in our report.
