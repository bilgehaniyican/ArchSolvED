# ArchSolvED

Orientation of educational building spaces have an impact on environmental parameters such as temperature and natural light.
These parameters influence students’ cognitive functions.
Designing educational buildings with complex building programs that have good environmental parameters is a hard task for architects.

ArchSolvED is a web application aimed to help architects in designing educational buildings.
It searches for the best layout regarding spatial orientation within a given set of school design parameters.
ArchSolvED employs a heuristic search algorithm with heuristics derived from architectural design principles and educational building design guidelines.

## Usage

### Running

Install dependencies from `requirements.txt`

```commandline
pip install -r requirements.txt
```

Run Flask server

```commandline
python main.py
```

### Preparation

Create a .dxf file of building site with side boundaries and set-back boundaries are drawn as a POLYGON and labeled `siteboundary` and `setbackboundary`.

Units in the file must be in meters.

Orientation of the site plan must be North facing up.

### Uplad Site Plan

In upload stage, the prepared .dxf file should be uploaded.

The sample file provided with the application can be used for demo purposes.

### School Type and Climate Selection

School type and climate data should be selected. The province the building site located in can also be selected instead of the province's climate type.

Floor count and classroom counts should be input. Classroom count is increments of 4, due to current education system in Turkiye.

ArchSolvED assesses student density for given parameters. Standard for density assessment can be chosen from Turksih and European standards.

### Building Program

A default building program is provided. It is possible to change sub-unit dimensions and counts to accomodate needs.

Circulation ratio to total sub-unit area can be selected.

Total building area is provided in this step.

### Circulation Drawing

In circulation drawing, the corridors of the school building is drawn.

Instructions are provided in the pop-up.

### Results

Solutions found are listed in this step.

It is possible to print suitable solutions.

## Acknowledgements

This software is developed as a part of the PhD thesis at Karabuk University.