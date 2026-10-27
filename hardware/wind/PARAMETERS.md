# Anemometer parameters

`anemometer.FCStd` now uses the **Parameters** spreadsheet (internal name
`Spreadsheet`). Edit values in column B in the INPUTS sections. Cells have named
aliases; the DERIVED section calculates assembly positions. All clearances called
"diametral" are differences of diameters, not radial gaps.

## Hub and arm alignment (updated)

The current model uses:

```text
Hub inside roof Z = ShaftTopZ
HubTopZ           = ShaftTopZ + HubRoofThickness
ArmBottomZ        = HubTopZ
```

The arm-interface bottom constraint uses `ArmBottomZ`; both arm-hole heights
also follow that alias. `HubTopBelowUpperBearingTop` is retained only as an
unused legacy input.

With the current saved inputs, the shaft top and hub inside roof are at 90.8 mm,
the hub top and arm bottom are at 94.8 mm, and the arm top is at 114.8 mm.
The hole centers are at 98.8 and 108.8 mm. Alignment was checked after reopening
and after a temporary +5 mm cavity-clearance change; all sketches remain fully
constrained and all bodies valid. The clearance was restored to your 25 mm value.

The sections below record the **initial migration** and its original defaults
and interference findings, not the latest user-edited dimensions or fit status.

## Enlarge the space above the PCB

Change **BearingToPcbClearance** from `12.2 mm` to, for example, `17.2 mm`.
This measures from the PCB's top surface to the lower bearing's underside.
It is not the unobstructed space below the retainer or around the shaft/magnet.

- Mount, PCB, magnet, and shaft lower end stay fixed.
- Both bearings and seats rise by 5 mm; their spacing stays unchanged.
- The cartridge cavity lengthens and its top rises by 5 mm.
- Hub, arm interface (including holes), and retainers rise by 5 mm.
- Shaft length increases by 5 mm.

The saved default remains `12.2 mm`: the migration does not apply an arbitrary
cavity enlargement. `CavityDiameter` controls the cavity diameter separately.
The lower external taper starts at `LowerTaperStartZ`, so increasing cavity height
also extends the middle outside section; the outer profile is not a rigidly
translated shell.

## Datums and dependencies

Mount top is Z=0. The original XZ-plane revolved sketches are retained: sketch X
is radius and sketch Y is assembly Z. Dimensions use spreadsheet expressions;
component placements remain unchanged except for the existing retainer clone.

```text
PcbTopZ             = PcbBottomGap + PcbThickness
CavityFloorZ        = PcbTopZ + PcbTopClearance
LowerBearingBottomZ = PcbTopZ + BearingToPcbClearance
LowerBearingTopZ    = LowerBearingBottomZ + BearingWidth
UpperBearingBottomZ = LowerBearingTopZ + BearingInnerGap
UpperBearingTopZ    = UpperBearingBottomZ + BearingWidth
ShaftTopZ           = UpperBearingTopZ + ShaftTopExtension
```

Important inputs:

| Alias | Default | Meaning |
|---|---:|---|
| BearingToPcbClearance | 12.2 mm | Main axial cavity control |
| CavityDiameter | 32.4 mm | Cavity inside diameter |
| BearingInnerGap | 40 mm | Between facing bearing surfaces, not center spacing |
| BearingWidth | 7 mm | Both bearing widths and seat depths |
| BearingOD | 22 mm | Both bearing outside diameters |
| ShaftDiameter | 8 mm | Shaft, bearing ID, nominal hub bore |
| BearingSeatDiametralClearance | 0.4 mm | Seat diameter minus bearing OD |
| PcbDiameter / PcbThickness | 40 / 1.6 mm | Board dimensions |
| PcbBottomGap / PcbTopClearance | 0.2 / 0.2 mm | Gap below board / above board at ledge |
| PcbPocketDiametralClearance | 0.4 mm | Pocket minus board diameter |
| MountDiameter | 46 mm | Mount and mating cartridge socket |
| MountSocketDiametralClearance | 0.4 mm | Socket minus mount diameter |
| RetainerThickness / RetainerAxialGap | 2 / 0.2 mm | Ring thickness / gap outside each bearing |
| MagnetToPcbGap | 3 mm | PCB top to magnet underside, not sensor-package gap |

The spreadsheet documents the remaining wall, socket, hub, arm, and magnet inputs.
Bearing seat depth, bearing spacing, and nominal shaft/bearing diameters are
shared. The PCB-to-mount radial step is no longer accidentally tied to the
cartridge's upper wall thickness. Signed axial constraints prevent solver flips
when changing cavity height in larger steps.

## Deliberate cleanup of previously unconstrained geometry

| Dimension | Before | Now |
|---|---:|---:|
| PCB underside Z | 0.162390 mm | 0.2 mm |
| PCB-to-bearing distance | 12.237610 mm | 12.2 mm |
| Hub skirt bottom Z | ≈19.2581 mm | 19 mm (48 mm overall skirt length) |
| Cartridge outer lower taper start Z | ≈8.6481 mm | 9 mm |
| Upper retainer underside Z | 68.156875 mm | 68.2 mm |
| Retainer thickness | 1.882293 mm | 2 mm |
| Lower retainer top Z | 14.039168 mm | 13.8 mm |
| Magnet underside Z | 4.950596 mm | 4.8 mm |

Bearing locations remain 14–21 mm and 61–68 mm at defaults. The retainer clone's
fixed -56 mm offset is replaced by a relationship between bearing faces; at
defaults it is -56.4 mm. All ten sketches are fully constrained.

## Validation and remaining design work

Validated using FreeCAD 1.1.0, including reopening the saved model:

- All sketches solve and are fully constrained; all nine bodies are valid and
  have positive volume.
- Cavity clearance changes to 10, 17.2, and 22.2 mm preserve the intended stack.
- Independent changes to bearing width (8), bearing inner gap (45), bearing OD
  (24), shaft diameter (9), cavity diameter (34.4), PCB diameter (42), mount
  diameter (48), and retainer thickness (3), in mm, recompute successfully.
- Bearing seats, PCB pocket, mount socket, and both retainer positions were
  numerically checked against the spreadsheet.
- Defaults were restored before saving.

These checks establish geometric validity, not mechanical suitability for every
parameter combination. Keep cavity diameter larger than seat diameter, PCB pocket
larger than cavity, and mount socket larger than PCB pocket. Maintain positive
walls and enough space for retainers and the outer tapers. Manufacturing fits
need validation for the actual material/process.

Existing interferences were found in the original model and remain:

- shaft/bearings with hub and arm interface;
- cartridge with hub and arm interface;
- hub with arm interface;
- magnet entirely overlapping the shaft (no magnet pocket modeled).

The original lower-retainer/bearing and lower-retainer/cartridge overlaps are
removed by the explicit ring thickness and axial gap. The hub's original top
position relative to the upper bearing was preserved, not redesigned.

This is the first-pass parameterization, not a full assembly rebuild. Shaft and
bearings still share the original `collar+bearing` body. Splitting hardware into
separate bodies, resolving the overlaps, adding a magnet pocket, and replacing
static exploded copies with links remain separate work. STEP exports and the
separate exploded-view document have not been regenerated.

`parameterize_anemometer.py` records the one-time migration and offers
`validate(document)` inside FreeCAD. Do not rerun `migrate` on the migrated model;
it requires the original empty spreadsheet and original constraint indices.
A pre-migration backup is saved as `anemometer.pre-parameters.FCBak`.
