"""
Copyright 2024 Olivier Stuker a.k.a. BinaryBorn
"""

from kakiprimitives import vec4, box, figure
from kakiutils import getBoundingBox

def pointInRect(rect: box, p: vec4):
  """Returns whether a given point is within a given rect.
  """
  if p.x >= rect.x0 and p.x < rect.x1:
    if p.y >= rect.y0 and p.y < rect.y1:
      return True
  return False

def edgeFunction(a: vec4, b: vec4, c: vec4):
  """Calculates a hint to the area spanned by the triangle ABC.

  Args:
    a (vec4): A
    b (vec4): B
    c (vec4): C
  
  Returns:
    float: >0 if ABC is CW and has an area, <0 if ABC is CCW and has an area, 0 if ABC has no area
  """
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def crossingNumber(poly: list[vec4], p: vec4):
  """Computes the crossing number for a given point in a polygon.

  Args:
    poly (list[vec4]): polygon
    p (vec4): point to test

  Returns:
    int: crossing number
  """
  cn = 0 # crossing number counter

  # loop through all edges of the polygon
  for i in range(len(poly)):
    p0 = poly[i-1] # -1 will address last item
    p1 = poly[i]
    # "upward" and "downward" mean inc/dec y respectively
    if ((p0.y <= p.y) and (p1.y > p.y)        # "upward" crossing
        or (p0.y > p.y) and (p1.y <= p.y)):   # "downward" crossing
      # compute x of edge-horizontal intersection
      cx = p0.x + (p.y - p0.y) / (p1.y - p0.y) * (p1.x - p0.x)
      # only count crossings to the right
      if p.x < cx:
        cn += 1

  return cn

def pointInFigureCn(figure: figure, p: vec4) -> bool:
  """Decides whether a point is within a figure using the crossing number algorithm, a.k.a. the even-odd fill rule.

  Args:
    figure (figure): figure
    p (vec4): point to test

  Returns:
    bool: true if point is in figure
  """
  cn = 0
  for pts in figure:
    # bounding box check
    bbox = getBoundingBox(pts)
    if bbox is not None and pointInRect(bbox, p):
      cn += crossingNumber(pts, p)
  return cn % 2 != 0


def windingNumber(poly: list[vec4], p: vec4) -> int:
  """Computes the winding number for a point in a polygon.

  Args:
    poly (list[vec4]): polygon
    p (vec4): point to test

  Returns:
    int: winding number
  """
  wn = 0 # winding number counter

  # loop through all edges of the polygon
  for i in range(len(poly)):
    p0 = poly[i-1] # -1 will address last item
    p1 = poly[i]
    # "upward" and "downward" mean inc/dec y respectively
    if (p0.y <= p.y):   # "upward" crossing candidate
      if (p1.y > p.y):  # actual "upward" crossing
        # crossing to the left
        if edgeFunction(p0, p1, p) > 0:
          wn += 1
    else:               # "downward" crossing candidate
      if (p1.y <= p.y): # actual "downward" crossing
        # crossing to the anti-left (a.k.a. right)
        if edgeFunction(p0, p1, p) < 0:
          wn -= 1

  return wn

def pointInFigureWn(figure: figure, p: vec4) -> bool:
  """Decides whether a point is within a figure using the winding number algorithm, a.k.a. the nonzero fill rule.

  Args:
    figure (figure): figure
    p (vec4): point to test

  Returns:
    bool: true if point is in figure
  """
  wn = 0
  for pts in figure:
    # bounding box check
    bbox = getBoundingBox(pts)
    if bbox is not None and pointInRect(bbox, p):
      wn += windingNumber(pts, p)
  return wn != 0


# scan line based point in polygon checks (optimization)

type slpipCrossing = tuple[list[vec4], list[vec4], bool]

class slpipScanLine:
  __slots__ = ['y', 'crossings']

  def __init__(self, y: float):
    self.y = y
    self.crossings: list[slpipCrossing] = []

def slpipScanFigure(figure: figure, y: float):
  scanline = slpipScanLine(y)

  for polygon in figure:
    for i in range(len(polygon)):
      p0 = polygon[i-1] # -1 will address last item
      p1 = polygon[i]
      # "upward" and "downward" mean inc/dec y respectively
      if (p0.y <= y):   # "upward" crossing candidate
        if (p1.y > y):  # actual "upward" crossing
          scanline.crossings.append((p0, p1, True))
      else:             # "downward" crossing candidate
        if (p1.y <= y): # actual "downward" crossing
          scanline.crossings.append((p0, p1, False))

  return scanline

def slpipCrossingNumber(scanline: slpipScanLine, x: float):
  cn = 0 # crossing number counter

  y = scanline.y

  # loop through all crossings
  for crossing in scanline.crossings:
    p0 = crossing[0]
    p1 = crossing[1]
    # < up/down crossing check already done >
    # compute x of edge-horizontal intersection
    cx = p0.x + (y - p0.y) / (p1.y - p0.y) * (p1.x - p0.x)
    # only count crossings to the right
    if x < cx:
      cn += 1

  return cn

def slpipPointInFigureCn(scanline: slpipScanLine, x: float):
  return slpipCrossingNumber(scanline, x) % 2 != 0

def slpipWindingNumber(scanline: slpipScanLine, x: float):
  wn = 0 # winding number counter

  y = scanline.y
  p = vec4(x, y)

  # loop through all crossings
  for crossing in scanline.crossings:
    p0 = crossing[0]
    p1 = crossing[1]
    # < up/down crossing check already done >
    if (crossing[2]):   # "upward" crossing
      # crossing to the left
      if edgeFunction(p0, p1, p) > 0:
          wn += 1
    else:               # "downward" crossing
      # crossing to the anti-left (a.k.a. right)
      if edgeFunction(p0, p1, p) < 0:
          wn -= 1

  return wn

def slpipPointInFigureWn(scanline: slpipScanLine, x: float) -> bool:
  return slpipWindingNumber(scanline, x) != 0