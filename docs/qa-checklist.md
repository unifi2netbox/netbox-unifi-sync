# QA Checklist (Production Readiness)

Checklisten gælder staging-validering før udrulning af v0.3.27. Markér kun checks,
der faktisk er udført. En grøn unit-test eller dry-run erstatter ikke en test af
den konkrete NetBox/PostgreSQL-, RQ- og UniFi-installation.

## 1. Installation og build

- [ ] NetBox-version og Python-runtime er kompatible med plugin/dependencies.
- [ ] Samme plugin-version er installeret i web og alle workers; `pip check` består.
- [ ] Ved Docker: custom image bygger, og `docker compose config` validerer opsætningen.
- [ ] Pending migrations er anvendt, og `manage.py check` består.
- [ ] Backup, tidligere image/package-pin og rollback-plan er tilgængelige.

## 2. Automatiske checks

- [ ] `ruff check netbox_unifi_sync/` består.
- [ ] `pytest -q` består; eventuelle skips og deres begrænsning er dokumenteret.
- [ ] `bandit -r netbox_unifi_sync/ -ll` består.
- [ ] `pip-audit -r requirements.txt` er kontrolleret.
- [ ] Ved release: `python -m build` og `twine check dist/*` består.
- [ ] Ved workflow-ændringer: `actionlint` består.

## 3. Rettigheder og secrets

- [ ] Controller credentials sættes i UI-felter eller via secret-referencer.
- [ ] TLS-verifikation er aktiv, og UniFi-kontoens rettigheder matcher behovet.
- [ ] MFA/password/token-værdier er redigeret ud af snapshots, audit og fejluddrag.
- [ ] Brugere uden sync-rettighed kan ikke enqueue et job.
- [ ] Cleanup kræver både sync-rettighed og `netbox_unifi_sync.run_cleanup`.
- [ ] En eventuel persisteret sessionsfil er beskyttet med `0600`.

## 4. Funktionel staging-test

- [ ] Controller test og dry-run består; fejl i databaseadgang giver fejlet preflight.
- [ ] Fuld sync opretter/opdaterer forventede devices og interfaces.
- [ ] To serials med samme display name forbliver adskilte ved create, rename og gentaget sync.
- [ ] `sync_prefixes=false` opretter ingen prefixes; IP'er får eksisterende parent-mask eller host-mask.
- [ ] Parallelle worker-tråde opretter ikke dublerede prefixes i samme proces.
- [ ] Importerede device types genbruges på SKU-varianter og bevarer curated specs ved normal sync.
- [ ] Nye power ports vises med korrekt tæller efter efterfølgende gemninger.
- [ ] To controllere med samme login og forskellige mappings bruger hvert sit NetBox-site.
- [ ] IPAM, VLAN/WLAN-relationer, klient-IP'er og change log er kontrolleret for aktiverede funktioner.
- [ ] Gentagen login/sync fungerer med cached sessions og relevante API-varianter.

## 5. Cleanup og drift

- [ ] Første fulde sync køres uden cleanup; dry-run forstås som preflight, ikke slettepreview.
- [ ] Cleanup er testet på en staging-kopi med kendt tenant/site/type-scope.
- [ ] Cleanup springes over ved flere credentials/mapping-grupper, mens normal sync fortsætter.
- [ ] Grace-perioden for stale devices forveksles ikke med beskyttelse af andre cleanup-kategorier.
- [ ] Scheduler, manuelle jobs og management commands overlapper ikke på tværs af processer.
- [ ] Workerlogs og run/audit-historik kan bruges til fejlsøgning uden at afsløre secrets.
- [ ] Eventuel specs-cache har en bevidst valgt, skrivbar placering.

## 6. Release og udrulning

- [ ] Alle tre versionsfiler og tag matcher; changelog er opdateret.
- [ ] GitHub Release og den selvstændige PyPI-publicering er hver verificeret.
- [ ] Installation af den publicerede version er verificeret.
- [ ] Kendte begrænsninger og staging-resultater er dokumenteret og gennemgået.
- [ ] Driftsansvarlig har godkendt udrulningen.

Se [upgrade](upgrade.md), [cleanup](cleanup.md) og [release](release.md).
