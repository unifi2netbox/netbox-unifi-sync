# Wiki source pages

Denne mappe indeholder GitHub Wiki-sider som Markdown-kilde. README er
vedligeholdelsesvejledning og skal ikke publiceres som en Wiki-side.
Opdatering af filerne her publicerer ikke automatisk den separate GitHub Wiki.

## Publicering

Efter review/merge af dokumentationen: klon eller opdatér Wiki-repositoriet,
kopiér de relevante sider, gennemgå diffen og push til dets aktuelle branch.
Eksempel fra plugin-repositoriets rod:

```bash
git clone https://github.com/unifi2netbox/netbox-unifi-sync.wiki.git /tmp/netbox-unifi-sync-wiki
for page in wiki/*.md; do
  if [ "$(basename "$page")" != "README.md" ]; then
    cp "$page" /tmp/netbox-unifi-sync-wiki/
  fi
done
git -C /tmp/netbox-unifi-sync-wiki diff --check
git -C /tmp/netbox-unifi-sync-wiki diff
git -C /tmp/netbox-unifi-sync-wiki add '*.md'
git -C /tmp/netbox-unifi-sync-wiki commit -m "Update v0.3.26 documentation"
git -C /tmp/netbox-unifi-sync-wiki push origin HEAD
```

Brug en ledig lokal mappe, eller opdatér en eksisterende klon først. Slet ikke
andre Wiki-sider ukritisk; gennemgå bevidst eventuelle omdøbninger/sletninger.
GitHub Wiki bruger et separat repository (`<repo>.wiki.git`), og filnavnene bliver
til sidenavne. `Home.md` og `_Sidebar.md` linker til de publicerede sider.

De fulde tekniske guides ligger i repository-mappen `docs/`; Wiki-siderne
opsummerer dem og linker til den kanoniske dokumentation.
