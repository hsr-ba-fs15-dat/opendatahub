/* ********************************************************************

Geokodierung mit MOPublic

Vorausssetzungen:
1. MOPublic-Daten (Ebene Gebäudeadressen, Tabelle Gebaeudeeingang (GEB_Gebaeudeeingang))
2. 'Meine' Addressen (Tabelle/Spreadsheet) gem. Vorlage (im CSV-Vormat: 'myaddresses.csv')
3. (Spatialite installiert: Start in cmd-Shell oder Batch: DOS>spatialite myaddresses.sqlite)

Ablauf:
* Start DOS> spatialite myaddresses.sqlite
* Importieren von myaddresses.csv in Tabelle myaddresses.
* Laden der Geokodierungs-Daten als Virtual Table (Gebaeudeeingang MOPublic).
* Erweitern von myaddresses mit geom-Attribut.
* Matching und Ergänzen von myaddresses mit Koordinaten.
* (Aufräumen => tbd.!)

Einschränkungen:
* myaddresses.csv ist fix vorgegeben u.a. mit Strasse_Nr und attr1. 
* Jedes weitere Attribut hat eine Anpassung dieses Skripts zur Folge.

Offene Fragen: 
* Besseres Matching bei leicht anders oder falsch geschriebenen Adressen (FTS und ev. C-Fn.).

***********************************************************************/
  

------------------
-- Meine Ausgangsdaten (myaddresses, noch ohne Geometrie)
------------------

-- Erzeuge leere Tabelle:
-- DROP TABLE myaddresses;
CREATE TABLE myaddresses (
  street_name_no TEXT, 
  plz INTEGER, 
  city TEXT,
  attr1 TEXT
);

-- Importiere myaddresses.csv
.headers ON
.separator ";"
.import myaddresses.csv myaddresses

SELECT rowid,* FROM myaddresses ORDER BY 1;

-- Eliminiere Header:
DELETE FROM myaddresses WHERE rowid=1;

SELECT rowid,* FROM myaddresses ORDER BY 1;

------------------
-- Die Geodaten von MOPublic: Tabelle gebaeudeeingang
-- 
-- Doku. Siehe Begleitinfo.pdf sowie MOpublic03_ili1.ili
--
------------------

-- Lade Geokodierungs-Daten:
CREATE VIRTUAL TABLE gebaeudeeingang 
  USING VirtualShape(GEB_Gebaeudeeingang, 'CP1252', 21781);

/*
PRAGMA table_info(gebaeudeeingang);
0|PKUID|INTEGER|0||0
1|Geometry|BLOB|0||0
2|TID|VARCHAR(20)|0||0
3|Street_of|VARCHAR(20)|0||0
4|Gueltigkei|VARCHAR(32)|0||0
5|IstOffizie|VARCHAR(32)|0||0
6|HoehenLage|VARCHAR(32)|0||0
7|Hausnummer|VARCHAR(12)|0||0
8|GebaeudeNa|VARCHAR(40)|0||0
9|GWR_EGID|VARCHAR(32)|0||0
10|GWR_EDID|VARCHAR(32)|0||0
11|Lokalisati|VARCHAR(60)|0||0
12|PLZ|VARCHAR(32)|0||0
13|Zusatzziff|VARCHAR(32)|0||0
14|Ortschafts|VARCHAR(40)|0||0
15|Stand_am|INTEGER|0||0
16|BFSNr|VARCHAR(32)|0||0

-- View gebaeudeeingang:
SELECT gwr_egid, lokalisati, hausnummer, plz, ortschafts FROM gebaeudeeingang LIMIT 10;

-- Test ohne einzufügen:
SELECT m.rowid,m.street_name_no,m.plz,m.city,m.attr1,'POINT('||ST_X(g.geometry)||' '||ST_Y(g.geometry)||')' FROM 
  myaddresses m LEFT JOIN gebaeudeeingang g ON 
    LOWER(REPLACE(m.street_name_no,'str.','strasse')||' '||m.plz||' '||m.city) = 
    LOWER(g.lokalisati||' '||trim(g.hausnummer)||' '||g.plz||' '||g.ortschafts); 
*/

------------------
-- Do the geocoding! Füge Geometrie-Werte zu  myaddresses hinzu.
--
-- Tricks: 
--  * Gross/Kleinsschreibung ist irrelevant
--  * "...str." wird zu "...strasse"
-- Probleme: 
--  * PLZ-Namen, die anders geschrieben sind.
--  * Addressen bei denen die Geb.Nr. fehlt (aber eigentlich vorhanden sein müsste).
--  * (weitere?)
------------------

SELECT AddGeometryColumn('myaddresses', 'geom', 21781, 'POINT', 'XY');

UPDATE myaddresses SET geom=(
  SELECT MakePoint(ST_X(g.geometry), ST_Y(g.geometry), 21781) FROM
    gebaeudeeingang g WHERE 
      LOWER(REPLACE(street_name_no,'str.','strasse')||' '||plz||' '||city) = 
      LOWER(g.lokalisati||' '||trim(g.hausnummer)||' '||g.plz||' '||g.ortschafts)
  );

/*  
-- View:
SELECT rowid,* FROM myaddresses ORDER BY 1;
*/

------------------
-- Was ist mit nicht gefundenen Adressen?
------------------

/*  
-- View:
SELECT rowid,street_name_no,plz,city,attr1,COALESCE(geom,'NO_GEOM_FOUND') FROM myaddresses ORDER BY 1;
*/

-- Set no_geom_found to middle of Switzerland!
-- Mittelpunkt der Schweiz (Älggi-Alp): POINT(660557 183337)
-- QGIS kann damit auch nicht gefundene Adressen anzeigen
UPDATE myaddresses SET geom=MakePoint(660557, 183337, 21781) WHERE geom IS NULL;

-- Aktualisiere Geometrie-Metadaten:
-- SELECT DiscardGeometryColumn('myaddresses', 'geom');
SELECT RecoverGeometryColumn('myaddresses', 'geom', 21781, 'POINT', 'XY');

-- Resultat:
SELECT rowid,* FROM myaddresses ORDER BY 1;


------------------
-- Aufräumen?
------------------
DROP TABLE gebaeudeeingang;

-- THE END.

