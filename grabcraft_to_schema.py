import csv, requests, json
from collections import defaultdict
from litemapy import Schematic, Region, BlockState

# Automatically map grabcraft blocks to schema blocks
def auto_block_map(grabcraft_block):
    def drop_state(b):
        parenthesis_loc = b.find(" (")
        if parenthesis_loc != -1:
            b = b[:parenthesis_loc]
        return b

    # Set the schema_block to grabcraft_block so that it's ready for later transformations
    schema_block = grabcraft_block
    # Remove the parenthesis
    schema_block = drop_state(schema_block)
    # Make all of the characters lowercase like in vanilla Minecraft block codes
    schema_block = schema_block.lower()
    # Removed all prepended spaces
    schema_block = schema_block.strip()
    # Replace all spaces with _ like in vanilla Minecraft block codes
    schema_block = schema_block.replace(' ', '_')
    # Replace some weird formatting regarding wood items
    schema_block = schema_block.replace("_wood_", '_')
    # Replace some weird formatting regarding wall mounted items
    schema_block = schema_block.replace("wall-mounted_", '')

    return f"minecraft:{ schema_block }"

class RenderObject:
    def __init__(self, url, north='north', block_map_file="blockmap.csv", dump=False):
        # Load the block map of predefined blocks
        self.block_map = {}
        with open(block_map_file, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                i += 1
                if i == 0:
                    continue
                self.block_map[row[1]] = row[2:]

        self.url = url[:url.find('#')] + "#general"
        self.north = north.lower()

        # Getting the webpage itself
        res = requests.get(self.url).text
        if (dump):
            with open("dump_page.html", "w", encoding='utf-8') as f:
                f.write(res)

        # The index for the renderObject's info
        render_object_i = res.find("myRenderObject")
        # The end index for getting the renderObject's string
        render_object_e = res.find('"', render_object_i)
        # Store the url to the render object
        render_object_url = "https://www.grabcraft.com/js/RenderObject/" + res[render_object_i:render_object_e]

        # Get the index for the name
        name_i = res.find("content-title")
        name_i = res.find(">", name_i) + 1
        # Get the end index for the name
        name_e = res.find("<", name_i)
        # Get the name
        self.name = res[name_i:name_e]

        # Get the index for the table containing the dimensions and tags
        table_i = res.find("object_properties")
        # Get the metadata
        rows = ("Width", "Height", "Depth", "Tags")
        meta = []
        for row in rows:
            # Get the row
            row_i = res.find(row, table_i)
            # Get the index for the value
            value_i = res.find('>', res.find("value", row_i)) + 1
            # Get the end index for the value
            value_e = res.find('<', value_i)
            # Get the value
            val = res[value_i:value_e]
            # If the value is a list split it to represent it as such
            if val.isdigit():
                val = int(val)
            elif val.find(", ") != -1:
                val = val.split(", ")
            # Add the values to the values list
            meta.append(val)
        self.tags = tuple(meta.pop())
        self.dims = tuple(meta)

        # Download render object's javascript
        ro_js = requests.get(render_object_url).text
        # Get the part of the javascript containing the JSON
        ro_text = ro_js[ro_js.find('{'):]
        # Convert it to a json
        ro_json = json.loads(ro_text)
        if dump:
            with open("dump_RenderObject.json", "w") as f:
                json.dump(ro_json, f, sort_keys=True, indent=4)

        # Unpack json into a flat list of blocks
        def json_iter(tree):
            for x, yz in tree.items():
                for y, z in yz.items():
                    for _, data in z.items():
                        yield data
        self.blocks = [(d["name"].strip(), int(d['x']), int(d['y']), int(d['z'])) for d in json_iter(ro_json)]

    def map_xz(self, x, z):
        match self.north:
            case "north":
                return x - 1, z - 1
            case "south":
                return self.dims[0] - x, self.dims[2] - z
            case "east":
                return self.dims[2] - z, x - 1
            case "west":
                return z - 1, self.dims[0] - x
            case _:
                exit(f"invalid north: '{north}'")

    def map_dims(self):
        match self.north:
            case "north" | "south":
                return self.dims
            case "east" | "west":
                return self.dims[::-1]
            case _:
                exit(f"invalid north: '{north}'")

    def map_block(self, grabcraft_block):
        if grabcraft_block in self.block_map:
            block = self.block_map[grabcraft_block]
            props = dict(zip(block[1::2], block[2::2]))
            return block[0], props
        else:
            block = auto_block_map(grabcraft_block)
            print('"' + grabcraft_block + '"', "->", '"' + block + '"')
            # return block
            exit()

    def to_schema(self):
        # Store the dimensions
        dims = self.map_dims()
        # Create the schema
        reg = Region(0, 0, 0, dims[0], dims[1], dims[2])
        schem = reg.as_schematic(name=self.name, author="GrabCraft", description=self.url)

        mat_list = defaultdict(int)

        # Fill the region with blocks
        for gc_block, gc_x, gc_y, gc_z in self.blocks:
            schema_y = gc_y - 1
            schema_x, schema_z = self.map_xz(gc_x, gc_z)

            schema_block, schema_props = self.map_block(gc_block)
            block = BlockState(schema_block, **schema_props)
            reg.setblock(schema_x, schema_y, schema_z, block)

            mat_list[schema_block[schema_block.find(":")+1:]] += 1

        return schem, mat_list

