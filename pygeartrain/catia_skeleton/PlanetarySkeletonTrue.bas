' ============================================================
' Planetary Gearbox TRUE Skeleton Generator for 3DExperience
' ============================================================
' Creates wireframe reference geometry (not solid bodies)
' - Points, axes, and pitch circles for sun, planets, ring
' - Use for skeleton-first modeling approach
'
' WORKING VERSION - 2026-01-31
' Key fix: AddNewCircleCtrRad needs 4 args (center, plane, geodesic, radius)
' ============================================================

Sub CATMain()

    Const Pi As Double = 3.14159265358979

    Dim editor As Object
    Dim part As Part

    Set editor = CATIA.ActiveEditor
    If editor Is Nothing Then
        MsgBox "No active editor.", vbExclamation
        Exit Sub
    End If

    Set part = editor.ActiveObject
    If part Is Nothing Then
        MsgBox "No active Part.", vbExclamation
        Exit Sub
    End If

    Dim hsFactory As HybridShapeFactory
    Set hsFactory = part.HybridShapeFactory

    Dim geoSet As HybridBody
    Set geoSet = part.HybridBodies.Add()
    geoSet.Name = "Skeleton"

    ' === DIMENSIONS (edit these for your gearset) ===
    Dim SunPD As Double: SunPD = 14       ' Sun pitch diameter
    Dim PlanetPD As Double: PlanetPD = 28 ' Planet pitch diameter
    Dim RingPD As Double: RingPD = 70     ' Ring pitch diameter
    Dim RingOD As Double: RingOD = 80     ' Ring outer diameter
    Dim OrbitR As Double: OrbitR = 21     ' Planet orbit radius = (SunPD + PlanetPD) / 2

    ' === REFERENCE GEOMETRY ===
    Dim refPlaneXY As Reference
    Set refPlaneXY = part.CreateReferenceFromObject(part.OriginElements.PlaneXY)

    ' Origin point
    Dim ptOrigin As HybridShapePointCoord
    Set ptOrigin = hsFactory.AddNewPointCoord(0, 0, 0)
    ptOrigin.Name = "POINT_ORIGIN"
    geoSet.AppendHybridShape ptOrigin

    Dim refOrigin As Reference
    Set refOrigin = part.CreateReferenceFromObject(ptOrigin)

    ' Z direction (normal to XY plane)
    Dim dirZ As HybridShapeDirection
    Set dirZ = hsFactory.AddNewDirection(refPlaneXY)

    ' Sun axis
    Dim axisSun As HybridShapeLinePtDir
    Set axisSun = hsFactory.AddNewLinePtDir(refOrigin, dirZ, -20, 20, False)
    axisSun.Name = "AXIS_SUN"
    geoSet.AppendHybridShape axisSun

    ' Sun pitch circle
    Dim circleSun As HybridShapeCircleCtrRad
    Set circleSun = hsFactory.AddNewCircleCtrRad(refOrigin, refPlaneXY, False, SunPD / 2)
    circleSun.Name = "CIRCLE_PITCH_SUN"
    geoSet.AppendHybridShape circleSun

    ' Ring pitch circle
    Dim circleRing As HybridShapeCircleCtrRad
    Set circleRing = hsFactory.AddNewCircleCtrRad(refOrigin, refPlaneXY, False, RingPD / 2)
    circleRing.Name = "CIRCLE_PITCH_RING"
    geoSet.AppendHybridShape circleRing

    ' Ring outer circle
    Dim circleRingOD As HybridShapeCircleCtrRad
    Set circleRingOD = hsFactory.AddNewCircleCtrRad(refOrigin, refPlaneXY, False, RingOD / 2)
    circleRingOD.Name = "CIRCLE_OUTER_RING"
    geoSet.AppendHybridShape circleRingOD

    ' Orbit circle (planet centers travel on this)
    Dim circleOrbit As HybridShapeCircleCtrRad
    Set circleOrbit = hsFactory.AddNewCircleCtrRad(refOrigin, refPlaneXY, False, OrbitR)
    circleOrbit.Name = "CIRCLE_ORBIT"
    geoSet.AppendHybridShape circleOrbit

    ' === PLANET GEOMETRY (3 planets at 120 deg spacing) ===
    Dim i As Integer
    Dim angle As Double
    Dim px As Double, py As Double

    For i = 1 To 3
        angle = (i - 1) * 2 * Pi / 3
        px = OrbitR * Cos(angle)
        py = OrbitR * Sin(angle)

        Dim ptPlanet As HybridShapePointCoord
        Set ptPlanet = hsFactory.AddNewPointCoord(px, py, 0)
        ptPlanet.Name = "POINT_PLANET_" & i
        geoSet.AppendHybridShape ptPlanet

        Dim refPlanet As Reference
        Set refPlanet = part.CreateReferenceFromObject(ptPlanet)

        Dim axisPlanet As HybridShapeLinePtDir
        Set axisPlanet = hsFactory.AddNewLinePtDir(refPlanet, dirZ, -20, 20, False)
        axisPlanet.Name = "AXIS_PLANET_" & i
        geoSet.AppendHybridShape axisPlanet

        Dim circlePlanet As HybridShapeCircleCtrRad
        Set circlePlanet = hsFactory.AddNewCircleCtrRad(refPlanet, refPlaneXY, False, PlanetPD / 2)
        circlePlanet.Name = "CIRCLE_PITCH_PLANET_" & i
        geoSet.AppendHybridShape circlePlanet
    Next i

    part.Update

    MsgBox "Skeleton created!", vbInformation

End Sub
