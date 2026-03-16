# grabcraft-to-schema
A Python library and its cli for converting grabcraft to schema (more specifically litematica schematic) files

To use the CLI run `cli.py` (it is also an example of how to use `RenderObject` class). For the list of arguments and optional switches run `cli.py -h`:

```
usage: cli [-h] [--version] [-f {north,south,east,west}] [-d] url

Download a blueprint from GrabCraft and convert it to a schematic in litematica format

positional arguments:
  url                   URL of the blueprint's page on GrabCraft website

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -f {north,south,east,west}
                        side of the original build facing the bottom of the GrabCraft blueprint
  -d                    dump the contents of the webpage and RenderObject json to a file
```

Upon succesful conversion CLI will output 2 files:
- a schema file in litematica format
- a text file with essential info about the structure, a list (histogram) of the blocks in GrabCraft format and a list of "materials" needed for the build.

## RenderObjects?
GrabCraft, instead of using things like .schematic or .litematic uses its own custom format called RenderObjects. If you're for instance, scraping the web and don't know what data you need to keep or generally want to be able to do stuff without having to worry about certain stuff breaking when dealing with GrabCraft's custom format, I recommend that you guys try to save `RenderObject`'s and their data. The `RenderObject.obj` field is what contains most of the data, which can easily be converted to a json as seen in the library itself since it's just a variable being set to a javascript dictionary which means that it's a json as soon as the javascript variable setting part is removed.

## Orientation
By the looks of it, orientation of each block is kept as it was in the original build from which the blueprint was created. On the other hand, blueprint itself is often re-oriented (publishing guidelines?) and coordinates for each block are assigned according to their location in the published blueprint. If blocks are positioned in a Minecraft world according to those coordinates, the structure will be oriented such that bottom side of the blueprint is facing north. If the orientation of the original build was different, all the individual blocks will be facing the wrong direction.

In order to have each block oriented correctly relative to the build, the library transforms the coordinates specified in the blueprint back to the coordinates of original build. The original orientation of the build is given by the compass in the upper right corner of the blueprint. Both CLI and RenderObject assume the north arrow of the compass is pointing down (toward the bottom of the blueprint). If it is different for particular blueprint, the cardinal direction displayed for the compass down arrow must be specified explicitly (`-f` option of CLI or `north` argument of the RenderObject constructor).

Technically it is possible to extract compass info from the webpage data automatically but the compass itself is unreliable. There are cases where it does not match the actual blocks orientation and in general must be verified manually anyway, e.g. [Small Wooden Cabin 4](https://www.grabcraft.com/minecraft/simple-starter-house-2/wooden-houses#blueprints).

## Block Mapping File
(under construction)

## Current Limitations:
As I only tested this on builds that I'm interested in personally, the library should not be expected to handle every single build offered by GrabCraft. If a structure cannot be converted properly it is likely due to one the following reasons:
- A block has not been seen before and is not present in the block mapping file `blockmap.csv`. Currently if an unknown block is encountered, the library tries to guess the block's identity but the success is not guaranteed and reconstructing the block states from the GrabCraft's free-form naming is practically impossible. The blockmap file with the new entry appended to the bottom of the list will be saved to `blockmap_new.csv`. Correct the ID/state of the new entry, rename the file to `blockmap.csv` and run CLI again.
- Even though present in `blockmap.csv`, many blocks are still missing neccessary states info and, when imported into Minecraft world, might be oriented wrongly, dropped as items and such.

## Documentation:
- `RenderObject(url, north='north', block_map=None, dump=False)`: the constructor to instantiate an object representing a GrabCraft's blueprint. `url` is link the blueprint's page, `north` is to specify build's orientation if different from blueprint's, `block_map` is for a custom blockmap object. If `dump` is True, GrabCraft webpage and RenderObject JSON file will be saved for inspection.
- `RenderObject.to_schema()`: the user method to convert GrabCraft's blueprint data into litematic schema
- `RenderObject.map_xz(x, z)`: internal method to map coordinates from blueprint to schema
- `RenderObject.map_dims()`: internal method to map build's dimensions from blueprint to schema
- `BlockMap(self, file="blockmap.csv")`: constructor for the blockmap object. Normally the new instance will be created by RenderObject automatically
- `BlockMap.__call__(block_id, block_name)`: the method to convert GrabCraft block names to Minecraft block IDs and states.
- `BlockMap.save(self, filename)`: the method to save blockmap data to CSV file.

## To Do
- After conversion, update 2-tall objects (doors, flowers) for consitency
- Convert to Bedrock's mcstructure format
