CREATE DATABASE "diematic";
CREATE USER "diematic" WITH PASSWORD 'mypassword';
GRANT ALL ON "diematic" TO "diematic";
CREATE RETENTION POLICY "one_day" ON "diematic" DURATION 24h REPLICATION 1 DEFAULT;
CREATE RETENTION POLICY "five_weeks" ON "diematic" DURATION 5w REPLICATION 1;
CREATE RETENTION POLICY "five_years" ON "diematic" DURATION 260w REPLICATION 1;

CREATE CONTINUOUS QUERY "cq_month" ON "diematic" BEGIN
  SELECT mean(/temperature/) AS "mean_1h", mean(/pressure/) AS "mean_1h", max(/temperature/) AS "max_1h", max(/pressure/) AS "max_1h"
  INTO "five_weeks".:MEASUREMENT
  FROM "one_day"."diematic"
  GROUP BY time(1h),*
END;

CREATE CONTINUOUS QUERY "cq_year" ON "diematic" BEGIN
  SELECT mean(/^mean_.*temperature/) AS "mean_24h", mean(/^mean_.*pressure/) AS "mean_24h", max(/^max_.*temperature/) AS "max_24h", max(/^max_.*pressure/) AS "max_24h"
  INTO "five_years".:MEASUREMENT
  FROM "five_weeks"."diematic"
  GROUP BY time(24h),*
END;

DROP CONTINUOUS QUERY cq_month ON diematic;
DROP CONTINUOUS QUERY cq_year ON diematic;