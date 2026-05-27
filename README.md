# NL2SQL-Tutor-Agent
SQL Query Learning Agent (inspired by PGExercises) is an intelligent system designed to transform natural language into functional SQL queries, with step-by-step explanations focused on learning, optimization, and best practices.

This project is inspired by practice-based platforms such as [PGExercises](https://pgexercises.com/), which present SQL problems as progressive challenges. However, unlike a traditional challenge-solving approach, this system is designed for active learning: the goal is not only to produce a correct query, but to understand how and why a particular SQL solution is constructed.


Example all modules tested

python -m app.temporal_testing

 python -m app.temporal_testing

[1] Async PostgreSQL session created
[2] Extracted 
[3] Columns extracted

====================================
RETRIEVED CONTEXT
====================================
{'schema': {'cd.members': {'columns': [{'name': 'memid', 'type': 'integer', 'primary_key': False, 'foreign_key': False}, {'name': 'surname', 'type': 'character varying', 'primary_key': False, 'foreign_key': False}, {'name': 'firstname', 'type': 'character varying', 'primary_key': False, 'foreign_key': False}]}, 'cd.facilities': {'columns': [{'name': 'facid', 'type': 'integer', 'primary_key': False, 'foreign_key': False}, {'name': 'name', 'type': 'character varying', 'primary_key': False, 'foreign_key': False}]}}, 'relationships': [], 'semantic_tables': {'bookings': {'description': 'Business table containing bookings information', 'domain_tags': ['database', 'business'], 'importance_score': 0.5}, 'facilities': {'description': 'Business table containing facilities information', 'domain_tags': ['database', 'business'], 'importance_score': 0.5}, 'members': {'description': 'Business table containing members information', 'domain_tags': ['database', 'business'], 'importance_score': 0.5}}, 'semantic_columns': {'bookings': [{'column': 'bookid', 'description': 'bookid field from bookings', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'facid', 'description': 'facid field from bookings', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'memid', 'description': 'memid field from bookings', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'starttime', 'description': 'starttime field from bookings', 'semantic_type': 'timestamp without time zone', 'synonyms': []}, {'column': 'slots', 'description': 'slots field from bookings', 'semantic_type': 'integer', 'synonyms': []}], 'facilities': [{'column': 'facid', 'description': 'facid field from facilities', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'name', 'description': 'name field from facilities', 'semantic_type': 'character varying', 'synonyms': []}, {'column': 'membercost', 'description': 'membercost field from facilities', 'semantic_type': 'numeric', 'synonyms': []}, {'column': 'guestcost', 'description': 'guestcost field from facilities', 'semantic_type': 'numeric', 'synonyms': []}, {'column': 'initialoutlay', 'description': 'initialoutlay field from facilities', 'semantic_type': 'numeric', 'synonyms': []}, {'column': 'monthlymaintenance', 'description': 'monthlymaintenance field from facilities', 'semantic_type': 'numeric', 'synonyms': []}], 'members': [{'column': 'memid', 'description': 'memid field from members', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'surname', 'description': 'surname field from members', 'semantic_type': 'character varying', 'synonyms': []}, {'column': 'firstname', 'description': 'firstname field from members', 'semantic_type': 'character varying', 'synonyms': []}, {'column': 'address', 'description': 'address field from members', 'semantic_type': 'character varying', 'synonyms': []}, {'column': 'zipcode', 'description': 'zipcode field from members', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'telephone', 'description': 'telephone field from members', 'semantic_type': 'character varying', 'synonyms': []}, {'column': 'recommendedby', 'description': 'recommendedby field from members', 'semantic_type': 'integer', 'synonyms': []}, {'column': 'joindate', 'description': 'joindate field from members', 'semantic_type': 'timestamp without time zone', 'synonyms': []}]}, 'joins': ['cd.bookings.memid = cd.members.memid', 'cd.bookings.facid = cd.facilities.facid', 'cd.members.recommendedby = cd.members.memid']}

====================================
MODULATED CONTEXT
====================================
DATABASE SCHEMA:
- cd.members (memid, surname, firstname)
- cd.facilities (facid, name)

KNOWN JOINS:
- cd.bookings.memid = cd.members.memid
- cd.bookings.facid = cd.facilities.facid
- cd.members.recommendedby = cd.members.memid

====================================
CONTEXT METRICS
====================================
Raw Context Size: 3486 chars
Modulated Context Size: 228 chars
Reduction: 93.46%
2026-05-27 01:32:50,467 INFO sqlalchemy.engine.Engine SELECT DISTINCT CONCAT(m.firstname,  ' ',  m.surname) AS member_name,  f.name AS facility_name
FROM cd.members m
JOIN cd.bookings b ON m.memid = b.memid
JOIN cd.facilities f ON b.facid = f.facid
WHERE f.name LIKE '%Tennis Court%'
ORDER BY member_name,  facility_name
LIMIT 100;
2026-05-27 01:32:50,467 INFO sqlalchemy.engine.Engine [generated in 0.00031s] ()

====================================
GENERATED SQL
====================================
SELECT DISTINCT CONCAT(m.firstname,  ' ',  m.surname) AS member_name,  f.name AS facility_name
FROM cd.members m
JOIN cd.bookings b ON m.memid = b.memid
JOIN cd.facilities f ON b.facid = f.facid
WHERE f.name LIKE '%Tennis Court%'
ORDER BY member_name,  facility_name
LIMIT 100;

====================================
EXPLANATION
====================================
This query:
1. Joins members to bookings via memid
2. Joins bookings to facilities via facid
3. Filters for facilities containing 'Tennis Court' in their name
4. Selects distinct combinations of member names (concatenated firstname+surname) and facility names
5. Orders results by member name then facility name
6. Limits to 100 results for safety

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
PIPELINE METRICS
====================================
Execution Time: 0.005s
LLM Time: 8.839s

====================================
PIPELINE SUCCESS
====================================
2026-05-27 01:32:50,472 INFO sqlalchemy.engine.Engine ROLLBACK
(venv) matthew@Matthew:~/TrainingSQL/Api_start$ 
