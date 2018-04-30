--UPDATE COUNT(*) from faces;
delete from faces;
delete from sqlite_sequence where name='faces';

-- UPDATE COUNT(*) from faces;
--delete from entities;
--delete from sqlite_sequence where name='entities';

--SELECT * FROM faces WHERE freebase_mid=='m.0gy1ww6' AND face_encoding IS NULL ORDER BY image_search_rank LIMIT 1;

vacuum;
SELECT freebase_mid, COUNT(*) FROM faces GROUP BY freebase_mid HAVING face_encoding IS NOT NULL;
--total rows 1155175  ->
-- distint freebase: 20000
--SELECT * from faces order by image_search_rank ;

SELECT COUNT(id) from faces; -- 1155175
SELECT COUNT(freebase_mid) from faces; -- 1155175
SELECT COUNT(distinct(freebase_mid)) from faces; -- 20000
SELECT COUNT(image_name) from faces;  -- 1155175
SELECT COUNT(distinct(image_name)) from faces; -- 1154706
SELECT image_name, COUNT(id) from faces group by image_name having COUNT(id) > 1;
--select * from faces where image_name='yLi4H7DS-FaceId-0' and image_search_rank=45;
--select * from faces where freebase_mid='m.09gbvrm' order by image_search_rank;--
SELECT freebase_mid, COUNT(*) as total, COUNT(face_encoding) as encodings FROM faces GROUP BY freebase_mid;
select count(face_encoding) from faces;

SELECT COUNT(*) from faces WHERE face_encoding IS NULL;

SELECT * from faces WHERE freebase_mid='m.02wb6yq';
select COUNT(*) from entities;
SELECT image_search_rank, freebase_mid from faces group by image_search_rank

select f.id, t.*
from faces f
join (
    select image_search_rank, freebase_mid, count(*) as qty
    from faces t
    group by image_search_rank, freebase_mid
    having count(*) = 1
) t on f.image_search_rank = t.image_search_rank and f.freebase_mid = t.freebase_mid
