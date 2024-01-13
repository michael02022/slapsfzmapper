# slapsfzmapper
CLI tool to generate SFZ mappings from a list of sample files

## Requirements
```
pip install natsort
```
(Used for os.sorted(), probably in the future this will be replaced)

## Usage
A very basic example:

Filename patterns inside the folder:
```
Hitsville_76_C2.wav
Hitsville_76_F#2.wav
Hitsville_76_C3.wav
Hitsville_76_F#3.wav
...
Hitsville_110_C2.wav
Hitsville_110_F#2.wav
Hitsville_110_C3.wav
Hitsville_110_F#3.wav
...
Pno-N-Elec_76_C2.wav
Pno-N-Elec_76_F#2.wav
Pno-N-Elec_76_C3.wav
Pno-N-Elec_76_F#3.wav
...
Pno-N-Elec_110_C2.wav
Pno-N-Elec_110_F#2.wav
Pno-N-Elec_110_C3.wav
Pno-N-Elec_110_F#3.wav
...
```
Commands for this case:
```
[command to run slapsfzmapper.py] -i "F:\my_samples\ensoniq-ts12" -sep "_" -ls "name velraw c4"
```
For more details, check the Wiki tab or MANUAL.md
