import sys, json, argparse
from collections import defaultdict
from grabcraft_to_schema import RenderObject

parser = argparse.ArgumentParser(prog='cli', description="Download a blueprint from GrabCraft and convert it to a schematic in litematica format")
parser.add_argument('--version', action='version', version='%(prog)s v1.00')
parser.add_argument('url', help="URL of the blueprint's page on GrabCraft website")
parser.add_argument('-f', choices= ['north', 'south', 'east', 'west'],
                          default = 'north',
                          help="side of the original build facing the bottom of the GrabCraft blueprint")
parser.add_argument('-d', action='store_true',
                          help="dump the contents of the webpage and RenderObject json to a file")

args = parser.parse_args()


# Download render object
robj = RenderObject(args.url, north=args.f, dump=args.d)
print("Done downloading!\n")

# Convert render object to MC schema
schem, materials_list = robj.to_schema()
if robj.block_map.updated > 0:
    print(f"Blockmap updated: {robj.block_map.updated}")
    robj.block_map.save("blockmap_new.csv")

out_name = robj.name.replace(" ", "_")

# Save the schema as litematica
schem.save(out_name + ".litematic")

# Save the schema statistics
with open(out_name + ".info", "w") as f:
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
        blocks_list[(block[1], block[0])] += 1
    for block in sorted(blocks_list):
        print(f"{blocks_list[block]:6d}", block, file=f)

    print(" -= materials =-", file=f)
    for material in sorted(materials_list):
        print(f"{materials_list[material]:6d}", material, file=f)
