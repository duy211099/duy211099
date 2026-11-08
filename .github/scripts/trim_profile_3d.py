"""Remove the language pie chart and the star/fork counters from the 3D contribution SVG.

The pie only covers public repos and reads as a stack label; the star/fork
counters show 0 because most work is in private org repos.
"""
import sys
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
G, TEXT = f"{{{NS}}}g", f"{{{NS}}}text"

path = sys.argv[1]
tree = ET.parse(path)
root = tree.getroot()

removed = 0
for parent in list(root.iter()):
    children = list(parent)
    for child in children:
        # Language pie: a group whose legend has <title> entries per language,
        # identified by the generator's fixed placement.
        if child.tag == G and child.get("transform", "").replace(" ", "") == "translate(40,520)":
            parent.remove(child)
            removed += 1
    # Stats row: keep the contributions count and the date range, drop the rest.
    texts = [c for c in children if c.tag == TEXT]
    if any((t.text or "").strip() == "contributions" for t in texts):
        keep_until = next(i for i, c in enumerate(children)
                          if c.tag == TEXT and (c.text or "").strip() == "contributions")
        for c in children[keep_until + 1:]:
            if c.tag == TEXT and c.get("class") == "fill-weak":
                continue  # date range
            parent.remove(c)
            removed += 1

if removed == 0:
    sys.exit(f"trim_profile_3d: nothing matched in {path}; generator output changed")
tree.write(path, encoding="utf-8", xml_declaration=False)
print(f"trim_profile_3d: removed {removed} elements from {path}")
