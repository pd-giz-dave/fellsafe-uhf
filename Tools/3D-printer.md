# Vertex Delta K8800
## 3D slicing software
 - Ultimaker Cura
 - It has a predefined printer for the Vertex Delta but its start gcode needs tweaking to change the end to this:

   G1 Z5 ; move up 5mm

   M400 ;wait for head to lift away from priming blob
   
   G1 X0 Y0 F2000 ; move to center, set feed rate
   
   M117 Vertex Delta printing

## 3D modelling software
 - OpenSCAD

