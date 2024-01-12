Here is the manual about how to use slapsfzmapper

## Getting started
The minimal requisites to run this program are:
* A folder input -- the path where contains samples*
* Separator -- write how is the separator to split the elements from the filename
* A root note -- it could be from the filename, sample metadata or none (percussion)
* A list -- the list that indicates which kind are the elements from the filename (based on the separator)

*Take note the samples won't be listed if are into subfolders

# 1. Folder input and output
## Arguments
### -i / --folderin
The **full path** where contains samples. It will search for samples. These files must have an extension. The current list of extensions are:
* wav
* aiff
* aif
* aifc
* flac
* ogg

### -o / --folderout
The usage of this one is special. Since it has different behaviours.
Keep in mind this will generate a `default_path` opcode and automatically generates the path to the samples for the sfz file.

#### Specifing the name for the generated sfz file
To enable this, you must to add the .sfz extension

This can be done in two ways:
##### -o "my\full\path\PIANO.sfz"
It means you want to save the generated sfz file into that specific path *AND* save it with the name `PIANO.sfz`

##### -o "PIANO.sfz"
It means you want to save the generated sfz file **a folder back** based on the input folder path with the name `PIANO.sfz`

##### Name is listed
if `name` is present in The List, it will add an index for each identified `name` in the folder:
```
PIANO-0.sfz
PIANO-1.sfz
PIANO-2.sfz
...
```
#### No specifing the name
if you don't specify the name, the name will be taken from two sources: the `name` present in The List or the folder name that contains the samples.

If you want to only specify the output folder path, a `-o "my\full\path"` is the answer.

If you don't use the `-o` command, then the generated sfz file will be saved **a folder back** based on the input folder path.

If you want to save the generated sfz file inside of the same input folder, then write `-o "*"`. For this use case, it won't use the `default_path` opcode

# 2. Separator
## -sep / --separator

This one is very simple, you assign a character as the separator between elements. This could be typically `"-"`, `"_"` or `" "`. Keep in mind if the filename contains several white spaces, these white spaces will be listed as elements (since the separator is one character long), so make sure to not have these extra spaces in the filename.

# 3. Spread
## -spr / --spread
The usage is `-spr "lo hi"`
This one means, how exactly you are going to spread the regions between root values (being root note and velocity note)? The first one is for key/root note, and the next one is for velocity. If you write only one (like `-spr "lo"`) this only affects the root note, while the velocity will use the default value. If you don't use this argument, it will use `lo hi` as default (since this is the most used and extended spread for samples.)

### Type of spreads
Depending of the spread, it will sound slighty different the mapping, but normally, the samples are meant to be spreaded as low. While for velocity, are meant to be spreaded as high.

#### lo (low)
Number is the start of the key/velocity (so it will split when the next sample starts).
```
           {here the split starts}
           v
------------------------
///////////|+++++|*****
///////////|+++++|*****
33333333333|66666|99999
________________________
| [] [] |  []  []  []  |
0    3     6     9     127
```

#### hi (high)
Number is the end of the key/velocity

```
    {here the split starts}
     v
------------------------
/////|+++++|***********
/////|+++++|***********
33333|66666|99999999999
________________________
| [] [] |  []  []  []  |
0    3     6     9     127
```
#### none
No spread, so the root key will be only one key of size for the region, same thing for velocity if applied.
```
------------------------
     |/|   |+|   |*|
     |/|   |+|   |*|
     |3|   |6|   |9|
________________________
| [] [] |  []  []  []  |
0    3     6     9     127
```
# 4. The List

## -ls / --list
Write which kind are the elements from the filename based on the separator. This list is very important due to the esential data that implies.
These lists of types of data only will be applied to filenames that has the same size of elements. For example, `-ls "name velraw c4"` is 3 elements of size, so it will only list the files that has the same size of elements in their filename:
```
================
Piano_110_g4.wav
================
-sep "_"
--------
-ls  "name velraw c4"
 |      v     v    v
 └>  Piano _ 110 _ g5.wav
           ^     ^
          sep   sep
OK -------------------

================
Piano_110_g4_rr2.wav
================
SKIPPED (ls has 3, this one 4)
```

The list of types of data are:
### Root key
#### root
The element is a number value, being the MIDI note of the sample, if it contains characters, those will be ignored (only will take the numbers.)
### cN (c3, c4, c5, ...)
This one is special, if you write `c4`, you are telling two things with this: this element is a **string** and, it represents a **note name** (C, D, E, F, G, A, B), and the center (MIDI note 60) for these note names is C4.

It will detect automatically the MIDI equivalent of this. And it does supports very odd ways of note naming, such as (these examples) `F#4`, `F4#`, `EF4`, `EB4`, (yeah, for flat notes they used b/B or f/F)... This also includes lower case and upper case variants.

Also, it can detect note names with trash/extra characters, like these ones:

`(EF4)`
`"G6dataBœ"`
`"D 2   "`
`"A 1"`
`"C# 1"`

### Velocity
#### velraw
Basically it works the same as root but applied to velocity numbers.

#### veldict
This is for a specific string associated with a velocity value based on a dictionary. The dictionaries are found in the folder `dict` which contains three common templates (the typical dynamic notations). The syntax is very simple:
```
string=number
```
the default dictionary is `veldict_a.txt`, and if you want to specify a dictionary, use `-dict` or `--dictionary` and then write `"your_custom_dict"` which is refering to `your_custom_dict.txt` in the folder `dict`

At the end It will be something like this: `-ls "root veldict" -dict "my_custom_dict"`

#### veldyn
This one is for non-specific velocity number, and more likely to a relative loudness (such as `vl1`, `vl2`, `vl3`, ...). This means the lower value is the quiest one and the higher value is the loudest one in a sort manner. So, the tool has to generate a curve based on this and give a velocity value based on the result. The default curve is linear, the user can configure this with the `-crv / --curve` argument.
#### -crv / --curve
You have some templates already, being `c-5` `c-4` `c-3` `c-2` `c-1` `c` `c+1` `c+2` `c+3` `c+4` `c+5` so you'll write `-crv "c+2"` to apply that curve for the velocities.
Also, you can use custom numbers like this: `-crv "0.76"`, but it's very tricky to use.
If you want a visual representation of these curves, check this website: https://sfzformat.com/misc/amp_velcurve_N_gen

Another feature is, sometimes, due the curve starting at 1, some mappings won't sound good. For this, the user can specify the floor for the curve, being a velocity value. If you write `-crv "c+2 20"` the curve will start at 20 instead of 1
### Naming
#### name
Another special feature, it let you assign a string or a series of strings elements as the name of the sfz file (and therefore the filenames/mappings are listed based on that name), this is useful when you have a ton of diferent variations or versions of the same instrument inside a folder or those are different instruments. This is the only element that you can use it more than one time.
```
================
SaxAlto_Sus_vl1_G4.flac
...
SaxAlto_Vib_vl1_G4.flac
...
SaxAlto_Stac_vl1_G4.flac
...
SaxTenor_Sus_vl1_G4.flac
...
SaxTenor_Vib_vl1_G4.flac
...
SaxTenor_Stac_vl1_G4.flac
...
================
-sep "_"
--------
-ls  "name name veldyn c4"
 |    v     v     v     v
 └>  Sax _ Sus _ vl1 _ G4.flac
         ^     ^     ^
        sep   sep   sep
OK -------------------
================
SaxAlto_Sus.sfz written.
SaxAlto_Vib.sfz written.
SaxAlto_Stac.sfz written.
SaxTenor_Sus.sfz written.
SaxTenor_Vib.sfz written.
SaxTenor_Stac.sfz written.
```
### Round Robin
#### rr
This is to assign a string element as the round robin of the sample and generates the round robin opcodes to each listed group inside of the sfz file. Works like `name` but modified for round robin.

### Miscellaneous
#### ign (ignore)
This one just ignores the string element. Normally data that we don't care or we don't need.

Here a silly example:
```
GT_xd_BASS_a0_f_rr1.wav
GT_xd_BASS_a0_f_rr2.wav
GT_xd_BASS_a0_f_rr3.wav
...
GT_xd_ELEC_a2_f_rr1.wav
GT_xd_ELEC_a2_f_rr2.wav
GT_xd_ELEC_a2_f_rr3.wav
...
=====================
-ls "name ign name c4 veldict rr"
----
GT_BASS.sfz
GT_ELEC.sfz
```

# 5. Options

## -opt / --options
Here you can see what kind of options you have to apply to the mapping.

Usage: `-opt "metadata fix-endloop"`

### metadata
Basically it reads the WAV (`smpl`) and AIFF (`MARK` `INST`) sample chunks inside of the file to get:
* start loop
* end loop
* root key
* tune
* loop mode (using the opcodes `loop_type` and `loop_mode`)

This also applies to FLAC files converted with the `--keep-foreign-metadata` argument.
https://xiph.org/flac/documentation_tools_flac.html

The reason for this is because not all SFZ players supports those chunks inside of FLAC files (like Sforzando), and I hate to store uncompressed PCM samples due to space issues. So I recommend to always embed this metadata in the SFZ file if you use FLAC files for the samples.

### fix-endloop
When it comes to sample converters, there is a confusion about the data stored in the loop points. It turns out, **you do not have to apply a +1 to the embedded value in the chunks**, because if you do that, the loop end up broken. That's why we have this. Basically it does a -1 to the `loop_end` opcode, so it restores the meant value for those kind of situations.

### byte-root
This will use the root MIDI value from the sample byte chunks instead of a string element from The List. Make sure all samples has a coherent value for this to work properly. No need to use root/cN when this is enabled.

### fix-tune
For some reason, sometimes the tune is inverted in the sample chunks. So this will invert them (from negative to positive and viceversa.)

### ignore-root
This one is for non-melodic instruments such as percussions and drums that has velocities and round robins. Pretty much it wil make the root of all listed samples as MIDI note 60. Combine it with `-spr "none"` so the sample will be only in `key=60`

### key-verbose
The spread `none` will generate the region with the opcode `key`. If for some reason you need the full opcodes `pitch_keycenter` `lokey` and `hikey`, this will enable that.

# 6. Miscellaneous

## Mono L / R samples
If the sample has the suffix `-L` `-R`, it will add the opcode `pan=` so we can have the intented stereo sample (like early AKAI libraries)
