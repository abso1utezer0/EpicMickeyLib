# EpicMickeyLib
A Python library for working with Epic Mickey's file structures and formats.

## Format Support

| Format Name | File Extension | Decompilation | Compilation | Notes |
| ----------- | -------------- | ------------- | ----------- | ----- |
| Scene/Palette | .bin | Yes | Yes | |
| Model | .nif | No | No | |
| Texture | _tex.nif | Yes | No | Besides a very rare, small NIF conversion bug, all that is left is implementing compilation for all the formats. |
| Animation | .hkx | Yes | Yes | |
| Skeleton | .hkx | Yes | Yes | |
| Sound | .wav | Yes | Yes | Possible with Memer's tool, which has gone missing. |
| Collision | .hkx | Yes(?) | Yes | Collision can only be decompiled to meshes, meaning the new collision file must be created from scratch using the mesh as a base. |
| Script | .lua | Yes | Yes | |
| Packfiles | .pak | Yes | Yes | The packfile format itself is fully supported, but research still needs to be done on how to grab the file list for the header with the correct ordering. |
| Collectible Database | .clb | Yes | Yes | |
| Dialog Dictionary | .dct | Yes | Yes | |
| Sequence | .bsq | No | No | Partial research has been done, but more is needed. |
| Subtitles | .sub | No | No | No research has been done. |
| Cooked Lighting | .lit_cooked | No | No | Not much research has been done. |
| AI Path Database | .obj | No | No | Not much research has been done. |
| AI Format | .hpd | No | No | No research has been done. |

## Installation

### Manual
1. Clone the repository.
2. Ensure the 'generated' folder from the latest [NifTools Blender plugin](https://cdn.discordapp.com/attachments/616397430027452416/1164658846816546887/blender_niftools_addon-v0.1.1-2023-10-19-57fdb417.zip) is in the root directory.
3. Run `python setup.py sdist` in the root directory.
4. Run `pip install dist/EpicMickeyLib-(version).tar.gz` in the root directory.
5. You're done! You can now import and use the library in your Python scripts.

### Pip
Coming soon.

## Usage
Coming soon.

## Credits
- Ryan "abso1utezer0" Koop - Creator
- AltruisticNut - Texture format research
- Candoran2/NifTools team - NIF file format support
- [OpenEM Discord](https://discord.com/invite/gFrXryz8Kf) - Testing, feedback, and support :heart: