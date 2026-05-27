# NL2SQL-Tutor-Agent
SQL Query Learning Agent (inspired by PGExercises) is an intelligent system designed to transform natural language into functional SQL queries, with step-by-step explanations focused on learning, optimization, and best practices.

This project is inspired by practice-based platforms such as [PGExercises](https://pgexercises.com/), which present SQL problems as progressive challenges. However, unlike a traditional challenge-solving approach, this system is designed for active learning: the goal is not only to produce a correct query, but to understand how and why a particular SQL solution is constructed.


Example all modules tested

python -m app.temporal_testing

[1] Async PostgreSQL session created
2026-05-27 00:11:26,566 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2026-05-27 00:11:26,567 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-05-27 00:11:26,584 INFO sqlalchemy.engine.Engine select current_schema()
2026-05-27 00:11:26,584 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-05-27 00:11:26,587 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2026-05-27 00:11:26,587 INFO sqlalchemy.engine.Engine [raw sql] ()
2026-05-27 00:11:26,589 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-05-27 00:11:26,590 INFO sqlalchemy.engine.Engine 
            SELECT
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = $1
            ORDER BY table_name;
        
2026-05-27 00:11:26,590 INFO sqlalchemy.engine.Engine [generated in 0.00042s] ('cd',)
[2] Extracted 3 tables
2026-05-27 00:11:26,614 INFO sqlalchemy.engine.Engine 
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,

                CASE
                    WHEN tc.constraint_type = 'PRIMARY KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_primary_key,

                CASE
                    WHEN fk.constraint_type = 'FOREIGN KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_foreign_key,

                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name

            FROM information_schema.columns c

            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name

            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.constraint_schema = tc.constraint_schema
                AND tc.constraint_type = 'PRIMARY KEY'

            LEFT JOIN information_schema.table_constraints fk
                ON kcu.constraint_name = fk.constraint_name
                AND kcu.constraint_schema = fk.constraint_schema
                AND fk.constraint_type = 'FOREIGN KEY'

            LEFT JOIN information_schema.constraint_column_usage ccu
                ON fk.constraint_name = ccu.constraint_name
                AND fk.constraint_schema = ccu.constraint_schema

            WHERE c.table_schema = $1
            AND c.table_name = $2

            ORDER BY c.ordinal_position;
        
2026-05-27 00:11:26,614 INFO sqlalchemy.engine.Engine [generated in 0.00028s] ('cd', 'bookings')
2026-05-27 00:11:26,657 INFO sqlalchemy.engine.Engine 
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,

                CASE
                    WHEN tc.constraint_type = 'PRIMARY KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_primary_key,

                CASE
                    WHEN fk.constraint_type = 'FOREIGN KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_foreign_key,

                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name

            FROM information_schema.columns c

            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name

            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.constraint_schema = tc.constraint_schema
                AND tc.constraint_type = 'PRIMARY KEY'

            LEFT JOIN information_schema.table_constraints fk
                ON kcu.constraint_name = fk.constraint_name
                AND kcu.constraint_schema = fk.constraint_schema
                AND fk.constraint_type = 'FOREIGN KEY'

            LEFT JOIN information_schema.constraint_column_usage ccu
                ON fk.constraint_name = ccu.constraint_name
                AND fk.constraint_schema = ccu.constraint_schema

            WHERE c.table_schema = $1
            AND c.table_name = $2

            ORDER BY c.ordinal_position;
        
2026-05-27 00:11:26,657 INFO sqlalchemy.engine.Engine [cached since 0.04281s ago] ('cd', 'facilities')
2026-05-27 00:11:26,670 INFO sqlalchemy.engine.Engine 
            SELECT
                c.table_schema,
                c.table_name,
                c.column_name,
                c.ordinal_position,
                c.data_type,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,

                CASE
                    WHEN tc.constraint_type = 'PRIMARY KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_primary_key,

                CASE
                    WHEN fk.constraint_type = 'FOREIGN KEY'
                    THEN TRUE
                    ELSE FALSE
                END AS is_foreign_key,

                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name

            FROM information_schema.columns c

            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name

            LEFT JOIN information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.constraint_schema = tc.constraint_schema
                AND tc.constraint_type = 'PRIMARY KEY'

            LEFT JOIN information_schema.table_constraints fk
                ON kcu.constraint_name = fk.constraint_name
                AND kcu.constraint_schema = fk.constraint_schema
                AND fk.constraint_type = 'FOREIGN KEY'

            LEFT JOIN information_schema.constraint_column_usage ccu
                ON fk.constraint_name = ccu.constraint_name
                AND fk.constraint_schema = ccu.constraint_schema

            WHERE c.table_schema = $1
            AND c.table_name = $2

            ORDER BY c.ordinal_position;
        
2026-05-27 00:11:26,670 INFO sqlalchemy.engine.Engine [cached since 0.05579s ago] ('cd', 'members')
[3] Columns extracted
2026-05-27 00:11:26,682 INFO sqlalchemy.engine.Engine 
            SELECT
                con.conname AS constraint_name,

                nsa.nspname AS source_schema,
                rel_a.relname AS source_table,
                att_a.attname AS source_column,

                nsb.nspname AS target_schema,
                rel_b.relname AS target_table,
                att_b.attname AS target_column

            FROM pg_constraint con

            JOIN pg_class rel_a
                ON rel_a.oid = con.conrelid

            JOIN pg_namespace nsa
                ON nsa.oid = rel_a.relnamespace

            JOIN pg_class rel_b
                ON rel_b.oid = con.confrelid

            JOIN pg_namespace nsb
                ON nsb.oid = rel_b.relnamespace

            JOIN pg_attribute att_a
                ON att_a.attrelid = con.conrelid
                AND att_a.attnum = ANY(con.conkey)

            JOIN pg_attribute att_b
                ON att_b.attrelid = con.confrelid
                AND att_b.attnum = ANY(con.confkey)

            WHERE con.contype = 'f'
            AND nsa.nspname = $1;
        
2026-05-27 00:11:26,682 INFO sqlalchemy.engine.Engine [generated in 0.00023s] ('cd',)
[4] Extracted 3 relationships
[5] Schema graph built
[6] Column graph built
/home/matthew/TrainingSQL/Api_start/app/temporal_testing.py:84: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  last_updated=datetime.utcnow()
/home/matthew/TrainingSQL/Api_start/app/temporal_testing.py:123: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  last_updated=datetime.utcnow()
[7] Semantic context built
[8] LLM context built
[9] SQL Generator initialized

====================================
QUESTION
====================================

            How can you produce a list of all members
            who have used a tennis court?

            Include in your output the name
            of the court, and the name
            of the member formatted
            as a single column.

            Ensure no duplicate data,
            and order by the member name
            followed by the facility name.
            
2026-05-27 00:11:37,962 INFO sqlalchemy.engine.Engine SELECT DISTINCT m.firstname || ' ' || m.surname AS member_name, f.name AS facility_name
FROM cd.bookings b
JOIN cd.facilities f ON b.facid = f.facid
JOIN cd.members m ON b.memid = m.memid
WHERE f.name LIKE '%Tennis Court%'
ORDER BY member_name, facility_name
LIMIT 100;
2026-05-27 00:11:37,962 INFO sqlalchemy.engine.Engine [generated in 0.00095s] ()

====================================
GENERATED SQL
====================================
SELECT DISTINCT m.firstname || ' ' || m.surname AS member_name, f.name AS facility_name
FROM cd.bookings b
JOIN cd.facilities f ON b.facid = f.facid
JOIN cd.members m ON b.memid = m.memid
WHERE f.name LIKE '%Tennis Court%'
ORDER BY member_name, facility_name
LIMIT 100;

====================================
EXPLANATION
====================================
This query:
1. Joins the bookings table with facilities and members tables
2. Filters for facilities containing 'Tennis Court' in their name
3. Combines member firstname and surname into a single column
4. Returns distinct combinations to avoid duplicates
5. Orders results by member name then facility name
6. Limits to 100 rows as a safety measure

====================================
RESULTS
====================================
{'member_name': 'Anne Baker', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Anne Baker', 'facility_name': 'Tennis Court 2'}
{'member_name': 'Burton Tracy', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Burton Tracy', 'facility_name': 'Tennis Court 2'}
{'member_name': 'Charles Owen', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Charles Owen', 'facility_name': 'Tennis Court 2'}
{'member_name': 'Darren Smith', 'facility_name': 'Tennis Court 2'}
{'member_name': 'David Farrell', 'facility_name': 'Tennis Court 1'}
{'member_name': 'David Farrell', 'facility_name': 'Tennis Court 2'}
{'member_name': 'David Jones', 'facility_name': 'Tennis Court 1'}
{'member_name': 'David Jones', 'facility_name': 'Tennis Court 2'}
{'member_name': 'David Pinker', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Douglas Jones', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Erica Crumpet', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Florence Bader', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Florence Bader', 'facility_name': 'Tennis Court 2'}
{'member_name': 'Gerald Butters', 'facility_name': 'Tennis Court 1'}
{'member_name': 'Gerald Butters', 'facility_name': 'Tennis Court 2'}
{'member_name': 'GUEST GUEST', 'facility_name': 'Tennis Court 1'}
{'member_name': 'GUEST GUEST', 'facility_name': 'Tennis Court 2'}

====================================
METRICS
====================================
Execution Time: 0.019s
LLM Time: 11.255s

====================================
PIPELINE SUCCESS
====================================
2026-05-27 00:11:37,981 INFO sqlalchemy.engine.Engine ROLLBACK
(venv) matthew@Matthew:~/TrainingSQL/Api_start$ 
