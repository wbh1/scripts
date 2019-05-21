# nocwiki_tkts
This script was made to generate ServiceNow tickets based off a CSV list containing 2,000 wiki articles that needed to be updated.

## Queries used to generate data
```sql
select title, c.lastmoddate from
content c
join spaces s on s.spaceid = c.spaceid
where c.contenttype = 'PAGE'
and c.prevver is null
and s.spacename like '%OCC Team%'
and c.title not like '%(decom%'
and c.content_status = 'current'
order by c.lastmoddate asc
fetch first 2000 rows only;
```

```sql
Copy (select title, c.lastmoddate from content c join spaces s on s.spaceid = c.spaceid where c.contenttype = 'PAGE' and c.prevver is null and s.spacename like '%OCC Team%' and c.lowertitle not like '%decom%' and c.content_status = 'current' order by c.lastmoddate asc fetch first 2000 rows only) To '/tmp/nocwiki.csv' With CSV DELIMITER ',';
```