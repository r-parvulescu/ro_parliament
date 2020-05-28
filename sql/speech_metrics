--add a year-month field to the elemental utterances table
update utterances_elemental 
set session_year_month = concat(date_part('year',session_date),'-',lpad(date_part('month',session_date)::text,2,'0'));

--create the metric-year-month table
create table yr_mo_word_metrics as
select
a.session_year_month,
sum(a.num_word) as sum_words_month,
min(coalesce(a.num_word,0)) as min_words,
max(a.num_word) as max_words
from utterances_elemental a, parliamentarians_elemental b 
where not
(bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte')
and a.utterer_url = b.url_stem group by a.session_year_month order by a.session_year_month;

-- figure out how many times each parliamentarian-legislature spoke in a given time month (if they didn't speak at all, it doesn't register). Make a table of number of utterances by dep-leg-year-month
create table yr_mo_dep_utterances as 
select 
session_year_month,
count(*) 
    from utterances_elemental a 
    group by a.session_year_month order by session_year_month
    inner join parliamentarians_elemental b 
    on a.utterer_url = b.url_stem
    as utterance_count; 
--the above is giving me a syntax error, can't figure it out

--add a column for the number of dep_legs who actually spoke in a certain year-month
alter table yr_mo_word_metrics add column num_users integer ;

--populate that new column
update yr_mo_word_metrics a 
set num_users = 
    (select count(*) 
    from yr_mo_dep_utterances b 
    where b.session_year_month = a.session_year_month 
    group by b.session_year_month)
;

--make table with number of words spoken by each dep-leg in one month, excluding nulls. Gives 30,662 entries, exclude formalistic speakers, i.e., presidents and vice-presidents of chamber of deputies
create table yr_mo_word_sum_dep as
select
a.session_year_month,
a.utterer_url,
a.utterer_last_name,
sum(a.num_word) as yr_mo_word_sum
from utterances_elemental a, parliamentarians_elemental b
where not
(bir_perm_role_1 = 'Preşedinte' OR bir_perm_role_1 = 'Vicepreşedinte' OR bir_perm_role_2 = 'Preşedinte' OR bir_perm_role_2 = 'Vicepreşedinte' OR bir_perm_role_3 = 'Preşedinte' OR bir_perm_role_3 = 'Vicepreşedinte' OR bir_perm_role_4 = 'Preşedinte' OR bir_perm_role_4 = 'Vicepreşedinte' OR bir_perm_role_5 = 'Preşedinte' OR bir_perm_role_5 = 'Vicepreşedinte' OR bir_perm_role_6 = 'Preşedinte' OR bir_perm_role_6 = 'Vicepreşedinte' OR bir_perm_role_7 = 'Preşedinte' OR bir_perm_role_7 = 'Vicepreşedinte' OR bir_perm_role_8 = 'Preşedinte' OR bir_perm_role_8 = 'Vicepreşedinte' OR bir_perm_role_9 = 'Preşedinte' OR bir_perm_role_9 = 'Vicepreşedinte' OR bir_perm_role_10 = 'Preşedinte' OR bir_perm_role_10 = 'Vicepreşedinte')
    and a.utterer_url = b.url_stem
    group by a.session_year_month, a.utterer_url,a.utterer_last_name;

--add a column for word_sum percentile value for each year-month. Ex. if the 30th percentile for 2001-02 is "248", it means that thirty percent of the people who spoke in February 2001 said less than 248 words.

alter table yr_mo_word_metrics 
add column null_value integer,
add column ten_perc integer,
add column thirty_perc integer,
add column median integer,
add column fifty_perc integer,
add column seventy_perc integer,
add column ninety_perc integer;

--compute and set the word count corresponding to the 10, 30, 50, 70, and 90 percentiles
update yr_mo_word_metrics a
set (ten_perc,thirty_perc,fifty_perc,seventy_perc,ninety_perc) = (
    (select percentile_cont(0.10) within group (order by yr_mo_word_sum) from yr_mo_word_sum_dep b where b.session_year_month = a.session_year_month group by session_year_month),
    (select percentile_cont(0.30) within group (order by yr_mo_word_sum) from yr_mo_word_sum_dep b where b.session_year_month = a.session_year_month group by session_year_month),
    (select percentile_cont(0.50) within group (order by yr_mo_word_sum) from yr_mo_word_sum_dep b where b.session_year_month = a.session_year_month group by session_year_month),
    (select percentile_cont(0.70) within group (order by yr_mo_word_sum) from yr_mo_word_sum_dep b where b.session_year_month = a.session_year_month group by session_year_month),
    (select percentile_cont(0.90) within group (order by yr_mo_word_sum) from yr_mo_word_sum_dep b where b.session_year_month = a.session_year_month group by session_year_month)  
);

--add a column of percentiles to yr_mo_word_sum_dep
alter table yr_mo_word_sum_dep
add column percentile text;

--and populate it with entries from yr_mo_word_metrics
update yr_mo_word_sum_dep a
set a.percentile =
    CASE 
--compare the number in the a.yr_mo_word_sum to the values in the percentile columns of yr_mo_word_metrics and return values of the form '<=10' or '50-69' in the percentile column of yr_mo_word_sum_dep
    (select percentile from yr_mo_word_metrics b 
    where a.session_year_month = b.session_year_month);

-- need a case here, which I can't figure out

--then 

CREATE TABLE parliamentarians_elemental_2 as 
SELECT DISTINCT * FROM parliamentarians_elemental;
