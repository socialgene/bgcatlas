from pathlib import Path

a=[i.name for i in Path("jsons").glob("*.json")]
a.sort()

with open('filenames.js', 'w') as f:
    _=f.write('var filenames=[')
    for i in a:
        _=f.write(f"'{i}',")
    _=f.write(']')
