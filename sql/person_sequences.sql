-- make the word sum table
CREATE TABLE dep_leg_url_word_sum (dep_leg_url text, word_sum integer);

-- populate it with rows computed from the utterances table, take only utterances after Jan 1, 1997 (elections were in Nov '96).  
insert into dep_leg_url_word_sum select utterer_url, sum(num_word) from utterances_elemental where session_date > '1997-01-01' group by utterer_url;

-- make a table of deputy-legislature features
create table dep_leg_word_sum as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer, bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                       
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url;

alter table dep_leg_word_sum
add column id SERIAL PRIMARY KEY,
add column percentile text;


--throw out 92-96 parliament, it has patchy transcripts (which is why I excluded those utterances above)
delete from dep_leg_word_sum where session_start < 1996;

--need to exclude the presidents and vice-presidents of the chamber because they say all the procedural things (11810780 words), which is about a quarter of total words (41151244), and we shouldn't conflate normal deputy talk with procedural formalism
select sum(word_sum) from dep_leg_word_sum;


-- As a rough cut I take P's and VP's out of the whole legislature. Later I'll be more fine-grained and only remove them from the particular sessions they chaired. 
delete from dep_leg_word_sum where 
    (bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte');

-- make a table of metrics for the words spoken in each legislature
create table leg_word_mtrcs as
select session_start, 
count(*) AS num_deps, 
sum(word_sum) as total_words_in_leg, 
round(avg(coalesce(word_sum,0)),2) AS average_words_per_dep,
round(stddev_pop(coalesce(word_sum,0)),2) as st_dev_words_per_dep,
min(coalesce(word_sum,0)) as min_words, 
max(coalesce(word_sum,0)) as max_words
from dep_leg_word_sum 
group by session_start order by session_start;

--make more columns for the percentiles
alter table leg_word_mtrcs
add column ten_perc integer, 
add column median integer, 
add column ninety_perc integer;
--I don't know how to nest expressions in sql yet, but I CAN make more tables

--for the session start in 1996
create table dlws_1996 as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer,
    bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                   
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url where session_start::integer >1995 and session_start::integer <2000;
---NB need to delete the vice-presidents el alia from each of these tables too, and make sure that I'm including null values in percentile counts

delete from dlws_1996 where 
bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte';


update leg_word_mtrcs 
set (ten_perc,median,ninety_perc) = (
    (select percentile_cont(0.10) within group (order by coalesce(word_sum,0)) from dlws_1996), 
    (select percentile_cont(0.50) within group (order by coalesce(word_sum,0)) from dlws_1996), 
    (select percentile_cont(0.90) within group (order by coalesce(word_sum,0)) from dlws_1996)
) 
where session_start = 1996;

-- for the session starting in 2000
create table dlws_2000 as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer,
    bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                   
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url where session_start::integer >1999 and session_start::integer <2004;
---NB need to delete the vice-presidents el alia from each of these tables too

delete from dlws_2000 where 
bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte';

update leg_word_mtrcs
set ten_perc = (select percentile_cont(0.10)  within group (order by coalesce(word_sum,0)) from dlws_2000) where session_start = 2000;

update leg_word_mtrcs
set median = (select percentile_cont(0.50)  within group (order by coalesce(word_sum,0)) from dlws_2000) where session_start = 2000;

update leg_word_mtrcs
set ninety_perc = (select percentile_cont(0.90)  within group (order by coalesce(word_sum,0)) from dlws_2000) where session_start = 2000;



--for the session starting in 2004
create table dlws_2004 as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer,
    bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                   
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url where session_start::integer >2003 and session_start::integer <2007;
---NB need to delete the vice-presidents el alia from each of these tables too

delete from dlws_2004 where 
bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte';

update leg_word_mtrcs
set ten_perc = (select percentile_cont(0.10)  within group (order by coalesce(word_sum,0)) from dlws_2004) where session_start = 2004;

update leg_word_mtrcs
set median = (select percentile_cont(0.50)  within group (order by coalesce(word_sum,0)) from dlws_2004) where session_start = 2004;

update leg_word_mtrcs
set ninety_perc = (select percentile_cont(0.90)  within group (order by coalesce(word_sum,0)) from dlws_2004) where session_start = 2004;


-- for the session starting in 2008
create table dlws_2008 as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer,
    bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                   
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url where session_start::integer >2007 and session_start::integer <2011;
---NB need to delete the vice-presidents el alia from each of these tables too

delete from dlws_2008 where 
bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte';

update leg_word_mtrcs
set ten_perc = (select percentile_cont(0.10)  within group (order by coalesce(word_sum,0)) from dlws_2008) where session_start = 2008;

update leg_word_mtrcs
set median = (select percentile_cont(0.50)  within group (order by coalesce(word_sum,0)) from dlws_2008) where session_start = 2008;

update leg_word_mtrcs
set ninety_perc = (select percentile_cont(0.90)  within group (order by coalesce(word_sum,0)) from dlws_2008) where session_start = 2008;


--for the session starting in 2012
create table dlws_2012 as 
select a.url_stem, b.word_sum, a.name, a.session_start::integer,
    bir_perm_role_1, bir_perm_role_2, bir_perm_role_3, bir_perm_role_4,
    bir_perm_role_5, bir_perm_role_6, bir_perm_role_7, bir_perm_role_8, bir_perm_role_9, bir_perm_role_10
from parliamentarians_elemental a                   
left join dep_leg_url_word_sum b
on a.url_stem = b.dep_leg_url where session_start::integer >2011 and session_start::integer <2015;
---NB need to delete the vice-presidents el alia from each of these tables too

delete from dlws_2012 where 
bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte';

update leg_word_mtrcs
set ten_perc = (select percentile_cont(0.10)  within group (order by coalesce(word_sum,0)) from dlws_2012) where session_start = 2012;

update leg_word_mtrcs
set median = (select percentile_cont(0.50)  within group (order by coalesce(word_sum,0)) from dlws_2012) where session_start = 2012;

update leg_word_mtrcs
set ninety_perc = (select percentile_cont(0.90)  within group (order by coalesce(word_sum,0)) from dlws_2012) where session_start = 2012;

--again, since I suq at subqueries just make more tables in order to figure out which deputy is in which percentile range
create table dep_leg_perc as
select a.name, a.session_start, a.word_sum, b.ten_perc, b.median, b.ninety_perc
from dep_leg_word_sum a 
left join leg_word_mtrcs b 
on a.session_start = b.session_start;

alter table dep_leg_perc
add column percentile text,
add column id SERIAL PRIMARY KEY;

update dep_leg_perc
set percentile = '<=10' where coalesce(word_sum,0) <= ten_perc;

update dep_leg_perc
set percentile = '11-49' where coalesce(word_sum,0) > ten_perc and word_sum < median;

update dep_leg_perc
set percentile = '50-89' where coalesce(word_sum,0) >= median and word_sum <ninety_perc;

update dep_leg_perc
set percentile = '>=90' where coalesce(word_sum,0) >= ninety_perc;

--finally make the table for exporting that has just the features I need
create table r_export(id serial PRIMARY KEY, name text, _1996 text, _2000 text, _2004 text, _2008 text, _2012 text);

--I populate this table through python scripts since I can't code in sql for shit and I don't have time to learn



1800-563-5954


-- had to do this, change column type so I can use date ranges

-- how to change integer column with date info to "date" type column
-- in this case, for utterances_element
alter table utterances_elemental alter column "session_date" type date using ("session_date"::text::date);

-- now for parliamentarians-elemental
alter table utterances_elemental alter column "session_date" type date using ("session_date"::text::date);

-- make a table where each row is a month's worth of sessions, and the columns are: year-month first session of month date, total number of deputies in the legislature at that time, last session of month date, number of sessions in month, total words in month, avg words per dep, st.dev words per dep, min words, max words, zero word speakers, tenth percentile (or words), 30th percentile, 50h percentile, 70th percentile, 90th percentile.

-- for each year, for each month, select the utterances whose session date fall between the first and last of the month. 
    --> count how many there are (i.e., number of sessions)
    --> get the smallest and largest of the date field (i.e., first and last sessions of the month)
    --> grouping by date range, sum the num_word column across the month
    --> grouping by deps, count how many distinct ones spoke that month
    --> add the number of deps in a legislature from the parliamentarian table
    --> compute average # of words per dep, once with only deps who spoke, and another time with all deps
    --> do the same for standard deviation
    --> get min and max word_num for all the utterances in that month 
    --> make distinct percentile categories, one for people who said less, another for those who said anything 1-10th percentile, 11-30, 31-50, 51-70, 71-90, 91 and above

