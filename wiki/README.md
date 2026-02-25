# Wiki source pages

Denne mappe indeholder Wiki-sider som Markdown-kilde.

## Publish til GitHub Wiki

```bash
cd /tmp
git clone git@github.com:unifi2netbox/netbox-unifi-sync.wiki.git
cd netbox-unifi-sync.wiki
rm -f *.md
cp /path/to/netbox-unifi-sync/wiki/*.md .
git add .
git commit -m "Update wiki pages"
git push origin main
```

Bemærk:

- GitHub Wiki bruger et separat git-repo (`<repo>.wiki.git`).
- Filnavne bliver til wiki-side-navne.
