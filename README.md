# grabcraft-to-schema
A Python library and its cli for converting grabcraft to schema (more specifically litematica schematic) files

To use the CLI run `cli.py` (It is also an example of how to use `RenderObject` class). Two command line arguments are expected:
- Original orientation of the structure in the blueprint; must be one of the 4 keywords - 'north', 'south', 'east' or 'west'. See details below.
- URL of the blueprint's page on the GrabCraft site

Upon succesful conversion CLI will output 2 files:
- a schema file in litematica format
- a text file with essential info about the structure, a list (histogram) of the blocks in GrabCraft format and a list of "materials" needed for the build.

## RenderObjects?
GrabCraft, instead of using things like .schematic or .litematic uses its own custom format called RenderObjects. If you're for instance, scraping the web and don't know what data you need to keep or generally want to be able to do stuff without having to worry about certain stuff breaking when dealing with GrabCraft's custom format, I recommend that you guys try to save `RenderObject`'s and their data. The `RenderObject.obj` field is what contains most of the data, which can easily be converted to a json as seen in the library itself since it's just a variable being set to a javascript dictionary which means that it's a json as soon as the javascript variable setting part is removed.

## Orientation
By the looks of it, orientation of each block is kept as it was in the original build from which the blueprint was created. On the other hand, blueprint itself is often re-oriented (publishing guidelines?) and coordinates for each block are assigned according to their location in the published blueprint. If blocks are positioned in a Minecraft world according to those coordinates, the structure will be oriented such that bottom side of the blueprint is facing north. If the orientation of the original build was different, all the individual blocks will be facing the wrong direction.

In order to have each block oriented correctly relative to the build, the library transforms the coordinates specified in the blueprint back to the coordinates of original build. The original orientation of the build is given by the compass in the upper right corner of the blueprint. The first argument to CLI must be the cardinal direction displayed for the compass arrow pointing down (toward the bottom of the blueprint).

Technically it is possible to extract compass info from the webpage data automatically but compass itself is unreliable. There are cases where blocks orientation does not match the compass, e.g. [Small Wooden Cabin 4](https://www.grabcraft.com/minecraft/simple-starter-house-2/wooden-houses#blueprints). I might still make it automatic later anyway, with optional override.

## Block Mapping File
(under construction)

## Current Limitations:
As I only tested this on builds that I'm interested in personally, the library should not be expected to handle every single build offered by GrabCraft. If a structure cannot be converted properly it is likely due to one the following reasons:
- A block has not been seen before and is not present in the block mapping file `blockmap.csv`. There is a piece of code in the library to try and guess the block's identity but it is disabled for now. The success is not guaranteed and reconstructing the block states from the GrabCraft's free-form naming is practically impossible. Currently if an unknown block is encountered, the library aborts the processing and exits. The name of the block and possible candidate for the official block ID are displayed on exit. Try to add them to `blockmap.csv` and run CLI again.
- Even though present in `blockmap.csv`, many blocks are still missing neccessary states info and, when imported into Minecraft world, might be oriented wrongly, dropped as items and such.

## Documentation:
- `RenderObject(url, north='north', block_map_file="blockmap.csv")`: the constructor to instantiate an object representing a GrabCraft's blueprint. `url` is link the blueprint's page, `north` is to specify build's orientation if different from blueprint's, `block_map_file` is for a custom block mapping file.
- `RenderObject.to_schema()`: the user method to convert GrabCraft's blueprint data into litematic schema
- `RenderObject.map_xz(x, z)`: internal method to map coordinates from blueprint to schema
- `RenderObject.map_dims()`: internal method to map build's dimensions from blueprint to schema
- `RenderObject.map_block(grabcraft_block)`: internal method to map a GrabCraft's block name to the corresponding Minecraft's block ID and its states

## To Do
- Generate block placement instructions for survival
- Convert to Bedrock's mcstructure format
