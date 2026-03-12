import sys, json
from collections import defaultdict
from grabcraft_to_schema import RenderObject

# Download render object
north, url = sys.argv[1:]
robj = RenderObject(url, north)
print("Done downloading!\n")

# Convert render object to MC schema
schem, materials_list = robj.to_schema()

out_name = robj.name.replace(" ", "_")

# Save the schema as litematica
schem.save(out_name + ".litematic")

# Save the schema statistics
with open(out_name + ".txt", "w") as f:
    print(" -= info =-", file=f)
    print("Name:", robj.name, file=f)
    print("URL:", robj.url, file=f)
    print("Facing North:", robj.north, file=f)
    print("Dimensions:", robj.dims, file=f)
    print("GrabCraft Tags:", robj.tags, file=f)
    print("Blocks:", len(robj.blocks), file=f)

    print(" -= blocks =-", file=f)
    blocks_list = defaultdict(int)
    for block in robj.blocks:
        blocks_list[block[0]] += 1
    for block in sorted(blocks_list):
        print(f"{blocks_list[block]:6d}", block, file=f)

    print(" -= materials =-", file=f)
    for material in sorted(materials_list):
        print(f"{materials_list[material]:6d}", material, file=f)
