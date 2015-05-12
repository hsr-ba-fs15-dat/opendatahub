/* ********************************************************************

Geokodierung mit MOPublic

Snippets / Work...

***********************************************************************/
  

MOPublic v1.1:
    TABLE Building_entrance =
      Street_of : ->Street_name; !! Relation c-mc
      Validity : [0 .. 1]; !! Designation under LookUp.Lookup_tables.Validity_type, only planned or valid object
      Pos : CoordP;
      Is_official_designation : [0 .. 1]; !! Designation under LookUp.Lookup_tables.Boolean_type
      Level : OPTIONAL [-99 .. 99];
      House_number : OPTIONAL TEXT*12;
      Name_of_house : OPTIONAL TEXT*40;
      RegBL_EGID : OPTIONAL [1 .. 999999999];
      RegBL_EDID : OPTIONAL [0 .. 99];
      Street_name : OPTIONAL TEXT*60;
      PostalCode : [1000 .. 9999];
      Additional_number : [0 .. 99];
      City : TEXT*40;
      State_of : DATE;
      FOSNr : OPTIONAL [0 .. 9999];
    NO IDENT
    END Building_entrance;

TID,   Street,V, PosX     PosY,     Is,L,No,N,EGID,EDID,Street_name, zip, A, City, State_of, FOSNr
133041 11703 1 612034.748 267494.308 1 @ 4 @ 454800 0 Alemannengasse 4058 0 Basel 20140208 2702

***

> spatialite myaddresses.sqlite

-- Prepare geocoding data table (FTS):

---- FILE building_entr_bs_city.csv with HEADER ----
east;north;No;EGID;Street_name;PLZ;City
612034.748;267494.308;4;454800;Alemannengasse;4058;Basel
...
---- END TABLE ----

CREATE TABLE building_entr (
  east DOUBLE, 
  north DOUBLE, 
  no NUMBER, 
  egid NUMBER, 
  street_name TEXT, 
  plz NUMBER, 
  city TEXT
);

.import building_entr.csv building_entr

SELECT * from building_entr;
SELECT no,street_name,egid,plz,city,east,north from building_entr;
SELECT egid,street_name,no,plz,city,east,north from building_entr;

-- Prepare geocoding lookup table (FTS):
-- Example schema
CREATE VIRTUAL TABLE geocoding USING fts3(subject, body);


INSERT INTO geocoding(docid, subject, body)
  SELECT cast(egid as number), street_name||' '||no||' '||plz||' '||city, 'POINT('||east||' '||north||')' FROM building_entr;
  
-- Optimize the internal structure of FTS table "geocoding".
INSERT INTO geocoding(geocoding) VALUES('optimize');
  
-- Example queries
SELECT docid,* FROM geocoding ORDER BY 1;
SELECT * FROM geocoding WHERE docid=454800;    
SELECT * FROM geocoding WHERE subject MATCH 'Alemannengasse 4 4058 Basel';

--- Prepare myaddresses
.import myaddresses.csv myaddresses

SELECT rowid,* FROM myaddresses ORDER BY 1;

--DROP TABLE myaddresses;
CREATE VIRTUAL TABLE myaddresses 
  USING VirtualText('myaddresses.csv','CP1252', 1, POINT, DOUBLEQUOTE, ';');
  -- Option: CP1252/UTF-8

PRAGMA table_info(myaddresses);
0|ROWNO|INTEGER|0||0
1|street_name_no|TEXT|0||0
2|plz|INTEGER|0||0
3|city|TEXT|0||0
4|attr1|TEXT|0||0


--**************************************************************
-- FTS!!!!
--**************************************************************

-- Prepare geocoding lookup table (FTS):
-- Example schema
CREATE VIRTUAL TABLE geocoding USING fts3(subject, body);

-- populate geocoding
-- DROP TABLE geocoding;
-- gwr_egid???
INSERT INTO geocoding(subject, body)
  SELECT 
    lokalisati||' '||trim(hausnummer)||' '||plz||' '||ortschafts, 
    'POINT('||ST_X(geometry)||' '||ST_Y(geometry)||')'
  FROM gebaeudeeingang;

-- Optimize the internal structure of FTS table "geocoding".
INSERT INTO geocoding(geocoding) VALUES('optimize');
  
-- Example queries
/*
SELECT docid,* FROM geocoding ORDER BY 1;
SELECT * FROM geocoding WHERE subject MATCH 'Alemannengasse 4 4058 Basel';
SELECT * FROM geocoding WHERE subject MATCH 'alemannengasse 4 4058 basel';
SELECT * FROM geocoding WHERE subject MATCH 'alemannengasse  4 4058 basel';
*/

-- Geocode!
--INSERT INTO myaddresses(ort, plz, strasse, hnr, kanton, quelle, geometry)
--  SELECT MakePoint(x_koord, y_koord, 21781), ort, plz, strasse, hnr, kanton, quelle
--  FROM adressen;

/*
SELECT rowid,street_name_no||' '||plz||' '||city FROM myaddresses;

SELECT street_name_no,plz,city,attr1,body
  FROM myaddresses, geocoding
  WHERE subject MATCH street_name_no||' '||plz||' '||city;
*/

UPDATE myaddresses SET geom_wkt=(
  SELECT body
    FROM geocoding
    WHERE subject MATCH street_name_no||' '||plz||' '||city
);

/*  
SELECT rowid,* FROM myaddresses ORDER BY 1;
SELECT count(*) FROM myaddresses WHERE geom_wkt IS NULL;
*/






--**************************************************************
-- WKT
--**************************************************************

-- ALTER TABLE myaddresses DROP COLUMN geom_wkt
ALTER TABLE myaddresses ADD COLUMN geom_wkt TEXT NULL;

-- Do the geocoding! Füge Geometrie-Werte ein.
UPDATE myaddresses SET geom_wkt=(
  SELECT 'POINT('||ST_X(g.geometry)||' '||ST_Y(g.geometry)||')' FROM 
    gebaeudeeingang g WHERE 
      LOWER(REPLACE(street_name_no,'str.','strasse')||' '||plz||' '||city) = 
      LOWER(g.lokalisati||' '||trim(g.hausnummer)||' '||g.plz||' '||g.ortschafts)
  );

-- Set no_geom_found to middle of Switzerland!
UPDATE myaddresses SET geom_wkt='POINT(660557.0 183337.0)' WHERE geom_wkt IS NULL;


