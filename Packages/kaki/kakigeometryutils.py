"""
Copyright 2024 Olivier Stuker a.k.a. BinaryBorn
"""

from kakiprimitives import vec4, mat4, box, figure, mesh
from kakiutils import getBoundingBox, copyPhenotype, transform, vecnorm, dotprod, crossprod, vecadd

def getFigureBoundingBox(figure: figure, round: bool = False) -> box:
  """Returns the bounding box of a whole figure.
  """
  points = []
  for pts in figure:
    points.extend(pts)
  return getBoundingBox(points, round)

def getMeshBoundingBox(mesh: mesh, round: bool = False) -> box:
  """Returns the bounding box of a mesh.
  """
  return getBoundingBox(mesh.verts, round)

def getPointsPlane(points: list[vec4]) -> vec4 | None:
  """Returns the plane equation for a list of points
  (assuming they're planar).
  The plane equation is nx*x + ny*y + nz*z = d

  Returns:
    vec4: x,y,z = plane normal (nx, ny, nz), w = scalar component (d)
  """
  i = 0
  pA: vec4
  pAB: vec4
  pB: vec4
  pC: vec4
  pBC: vec4
  for point in points:
    if i == 0:
      pA = point
      i += 1
    elif i == 1:
      pB = point
      pAB = vec4(pB.x - pA.x, pB.y - pA.y, pB.z - pA.z)
      i += 1
    else:
      pC = point
      pBC = vec4(pC.x - pB.x, pC.y - pB.y, pC.z - pB.z)
      cross = crossprod(pAB, pBC)
      norm = vecnorm(cross)
      # if that product has a length, we're done
      if norm > 0:
        # normalize cross product to make it a norm vector
        cross.x /= norm
        cross.y /= norm
        cross.z /= norm
        cross.w = dotprod(cross, pA)
        return cross

def getFigurePlane(figure: figure) -> vec4 | None:
  """Returns the plane equation for a figure
  (assuming it's planar).
  The plane equation is nx*x + ny*y + nz*z = d

  Returns:
    vec4: x,y,z = plane normal (nx, ny, nz), w = scalar component (d)
  """
  for polygon in figure:
    norm = getPointsPlane(polygon)
    if norm is not None:
      return norm

def transformPoints(points: list[vec4], t: mat4) -> None:
  """Transforms all points in list in-place.
  """
  for i in range(len(points)):
    points[i] = transform(points[i], t)

def transformFigure(figure: figure, t: mat4) -> None:
  """Transforms a figure in-place.
  """
  for pts in figure:
    transformPoints(pts, t)

def transformMesh(mesh: mesh, t: mat4) -> None:
  """Transforms a mesh in-place.
  """
  transformPoints(mesh.verts, t)
  # TODO: inverse transpose matrix
  # TODO: tn = inverseTranspose(t), transformPoints(mesh.normals, tn)

def clonePoints(points: list[vec4]) -> list[vec4]:
  """Returns a clone of a list of points, all points cloned.
  """
  clone = []
  for p in points:
    clone.append(vec4(p.x, p.y, p.z, p.w))
  return clone

def cloneFigure(figure: figure) -> figure:
  """Returns a clone of given figure.
  """
  clone = []
  for pts in figure:
    clone.append(clonePoints(pts))
  return clone

def cloneMesh(msh: mesh) -> mesh:
  """Returns a clone of given mesh.
  """
  clonedVerts = clonePoints(msh.verts)
  clonedTris = [tri.copy() for tri in msh.tris]
  clonedPhenos = [copyPhenotype(p) for p in msh.phenos]

  return mesh(clonedVerts, clonedPhenos, clonedTris)

def perspectiveDividePoints(points: list[vec4]) -> None:
  """Applies the perspective projection to a list of points.
  """
  for p in points:
    w = p.w
    # undocumented safety feature: prevent division by 0
    if w <= 1e-10:
      w = 1e-10
    p.x /= w
    p.y /= w
    p.z /= w

def perspectiveDivideFigure(figure: figure) -> None:
  """Applies the perspective projection to a figure.
  """
  for pts in figure:
    perspectiveDividePoints(pts)

def perspectiveDivideMesh(mesh: mesh) -> None:
  """Applies the perspective projection to a mesh.
  """
  perspectiveDividePoints(mesh.verts)

def updateNormalsMesh(mesh: mesh) -> None:
  """Updates the normal vectors in a mesh based on these simple rules
  * for every triangle, add the triangle's normal to each vertex
  * if a vertex is shared across multiple triangles, its normal will be averaged
  """
  for tri in mesh.tris:
    i0 = tri[0]
    i1 = tri[1]
    i2 = tri[2]
    v0 = mesh.verts[i0]
    v1 = mesh.verts[i1]
    v2 = mesh.verts[i2]
    normal = getPointsPlane([v0, v1, v2])
    if normal is None: normal = vec4(0, 0, 0)
    mesh.normals[i0] = vecadd(mesh.normals[i0], normal)
    mesh.normals[i1] = vecadd(mesh.normals[i1], normal)
    mesh.normals[i2] = vecadd(mesh.normals[i2], normal)