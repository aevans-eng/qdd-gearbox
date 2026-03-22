' ============================================================
' Planetary Gearbox Skeleton Generator for 3DExperience CATIA
' ============================================================
' Creates simplified cylinder geometry for gearbox planning
' Reads parameters from parameters.txt in the same folder
'
' Usage:
' 1. Open a new Part in 3DExperience CATIA
' 2. Run this macro
' 3. Select the parameters.txt file when prompted
' ============================================================

Option Explicit

' Global parameters (read from file)
Dim Module As Double
Dim FaceWidth As Double
Dim PlanetCount As Integer
Dim SunPitchDiameter As Double
Dim SunTeeth As Integer
Dim PlanetPitchDiameter As Double
Dim PlanetTeeth As Integer
Dim RingPitchDiameter As Double
Dim RingTeeth As Integer
Dim RingWallThickness As Double
Dim CarrierDiameter As Double
Dim CarrierThickness As Double
Dim GearZPosition As Double
Dim CarrierZPosition As Double

' CATIA objects
Dim CATIA As Application
Dim partDoc As PartDocument
Dim part As Part
Dim hybridBodies As HybridBodies
Dim hybridBody As HybridBody
Dim hybridShapeFactory As HybridShapeFactory
Dim shapeFactory As ShapeFactory
Dim bodies As Bodies
Dim Pi As Double

Sub CATMain()
    Pi = 3.14159265358979

    ' Get active document (3DExperience method)
    On Error Resume Next
    Set partDoc = CATIA.ActiveEditor.ActiveObject
    On Error GoTo 0

    If partDoc Is Nothing Then
        MsgBox "Please open a Part document first.", vbExclamation
        Exit Sub
    End If

    Set part = partDoc.Part
    Set shapeFactory = part.ShapeFactory
    Set hybridShapeFactory = part.HybridShapeFactory
    Set bodies = part.Bodies

    ' Prompt for parameters file
    Dim paramFile As String
    paramFile = CATIA.FileSelectionBox("Select parameters.txt", "*.txt", CatFileSelectionModeOpen)

    If paramFile = "" Then
        MsgBox "No file selected. Exiting.", vbExclamation
        Exit Sub
    End If

    ' Read parameters
    If Not ReadParameters(paramFile) Then
        MsgBox "Error reading parameters file.", vbCritical
        Exit Sub
    End If

    ' Validate planetary gear relationship
    Dim expectedRingTeeth As Integer
    expectedRingTeeth = SunTeeth + 2 * PlanetTeeth
    If RingTeeth <> expectedRingTeeth Then
        Dim msg As String
        msg = "Warning: Ring teeth (" & RingTeeth & ") doesn't match Sun + 2*Planet (" & expectedRingTeeth & ")." & vbCrLf
        msg = msg & "Continue anyway?"
        If MsgBox(msg, vbYesNo + vbQuestion) = vbNo Then
            Exit Sub
        End If
    End If

    ' Calculate orbit radius (center distance sun to planet)
    Dim orbitRadius As Double
    orbitRadius = (SunPitchDiameter + PlanetPitchDiameter) / 2

    ' Create geometry
    Call CreateSunGear
    Call CreatePlanetGears(orbitRadius)
    Call CreateRingGear

    If CarrierDiameter > 0 And CarrierThickness > 0 Then
        Call CreateCarrier(orbitRadius)
    End If

    part.Update

    MsgBox "Planetary skeleton created successfully!" & vbCrLf & vbCrLf & _
           "Sun: " & SunPitchDiameter & "mm PD" & vbCrLf & _
           "Planets: " & PlanetCount & "x " & PlanetPitchDiameter & "mm PD" & vbCrLf & _
           "Ring: " & RingPitchDiameter & "mm PD" & vbCrLf & _
           "Orbit Radius: " & orbitRadius & "mm", vbInformation
End Sub

Function ReadParameters(filePath As String) As Boolean
    On Error GoTo ErrorHandler

    Dim fso As Object
    Dim file As Object
    Dim line As String
    Dim parts() As String
    Dim paramName As String
    Dim paramValue As String

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set file = fso.OpenTextFile(filePath, 1) ' 1 = ForReading

    Do While Not file.AtEndOfStream
        line = Trim(file.ReadLine)

        ' Skip comments and empty lines
        If Len(line) > 0 And Left(line, 1) <> "#" Then
            If InStr(line, "=") > 0 Then
                parts = Split(line, "=")
                paramName = Trim(parts(0))
                paramValue = Trim(parts(1))

                Select Case paramName
                    Case "Module": Module = CDbl(paramValue)
                    Case "FaceWidth": FaceWidth = CDbl(paramValue)
                    Case "PlanetCount": PlanetCount = CInt(paramValue)
                    Case "SunPitchDiameter": SunPitchDiameter = CDbl(paramValue)
                    Case "SunTeeth": SunTeeth = CInt(paramValue)
                    Case "PlanetPitchDiameter": PlanetPitchDiameter = CDbl(paramValue)
                    Case "PlanetTeeth": PlanetTeeth = CInt(paramValue)
                    Case "RingPitchDiameter": RingPitchDiameter = CDbl(paramValue)
                    Case "RingTeeth": RingTeeth = CInt(paramValue)
                    Case "RingWallThickness": RingWallThickness = CDbl(paramValue)
                    Case "CarrierDiameter": CarrierDiameter = CDbl(paramValue)
                    Case "CarrierThickness": CarrierThickness = CDbl(paramValue)
                    Case "GearZPosition": GearZPosition = CDbl(paramValue)
                    Case "CarrierZPosition": CarrierZPosition = CDbl(paramValue)
                End Select
            End If
        End If
    Loop

    file.Close
    ReadParameters = True
    Exit Function

ErrorHandler:
    ReadParameters = False
End Function

Sub CreateSunGear()
    Dim body As body
    Set body = bodies.Add()
    body.Name = "Sun_Gear_PD" & SunPitchDiameter

    Call CreateCylinder(body, 0, 0, GearZPosition, SunPitchDiameter, FaceWidth, "Sun")
End Sub

Sub CreatePlanetGears(orbitRadius As Double)
    Dim i As Integer
    Dim angle As Double
    Dim x As Double, y As Double
    Dim body As body

    For i = 0 To PlanetCount - 1
        angle = (2 * Pi * i) / PlanetCount
        x = orbitRadius * Cos(angle)
        y = orbitRadius * Sin(angle)

        Set body = bodies.Add()
        body.Name = "Planet_" & (i + 1) & "_PD" & PlanetPitchDiameter

        Call CreateCylinder(body, x, y, GearZPosition, PlanetPitchDiameter, FaceWidth, "Planet" & (i + 1))
    Next i
End Sub

Sub CreateRingGear()
    Dim body As body
    Set body = bodies.Add()
    body.Name = "Ring_Gear_PD" & RingPitchDiameter

    Dim outerDiameter As Double
    outerDiameter = RingPitchDiameter + 2 * RingWallThickness

    Call CreateHollowCylinder(body, 0, 0, GearZPosition, RingPitchDiameter, outerDiameter, FaceWidth, "Ring")
End Sub

Sub CreateCarrier(orbitRadius As Double)
    Dim body As body
    Set body = bodies.Add()
    body.Name = "Carrier"

    ' Create main carrier disc
    Call CreateCylinder(body, 0, 0, CarrierZPosition, CarrierDiameter, CarrierThickness, "CarrierDisc")

    ' Optionally add planet bore representations (as pockets)
    ' For now, just the disc
End Sub

Sub CreateCylinder(body As body, x As Double, y As Double, z As Double, diameter As Double, height As Double, namePrefix As String)
    Dim sketches As Sketches
    Dim sketch As sketch
    Dim factory2D As Factory2D
    Dim circle As Circle2D
    Dim pad As pad

    ' Create reference plane offset from XY
    Dim refPlane As Reference
    Dim offsetPlane As HybridShapePlaneOffset

    Set refPlane = part.OriginElements.PlaneXY

    If z <> 0 Then
        Set offsetPlane = hybridShapeFactory.AddNewPlaneOffset(refPlane, z, False)
        offsetPlane.Name = namePrefix & "_Plane"

        Dim hybridBody1 As HybridBody
        On Error Resume Next
        Set hybridBody1 = part.HybridBodies.Item("Construction")
        On Error GoTo 0
        If hybridBody1 Is Nothing Then
            Set hybridBody1 = part.HybridBodies.Add()
            hybridBody1.Name = "Construction"
        End If
        hybridBody1.AppendHybridShape offsetPlane

        Set refPlane = part.CreateReferenceFromObject(offsetPlane)
    End If

    ' Create sketch
    Set sketches = body.Sketches
    Set sketch = sketches.Add(refPlane)
    sketch.Name = namePrefix & "_Sketch"

    Set factory2D = sketch.OpenEdition()

    ' Create circle at offset position
    Set circle = factory2D.CreateClosedCircle(x, y, diameter / 2)

    sketch.CloseEdition

    ' Create pad
    Set pad = shapeFactory.AddNewPad(sketch, height)
    pad.Name = namePrefix & "_Cylinder"
    pad.FirstLimit.Dimension.Value = height
End Sub

Sub CreateHollowCylinder(body As body, x As Double, y As Double, z As Double, innerDiameter As Double, outerDiameter As Double, height As Double, namePrefix As String)
    Dim sketches As Sketches
    Dim sketch As sketch
    Dim factory2D As Factory2D
    Dim outerCircle As Circle2D
    Dim innerCircle As Circle2D
    Dim pad As pad

    ' Create reference plane offset from XY
    Dim refPlane As Reference
    Dim offsetPlane As HybridShapePlaneOffset

    Set refPlane = part.OriginElements.PlaneXY

    If z <> 0 Then
        Set offsetPlane = hybridShapeFactory.AddNewPlaneOffset(refPlane, z, False)
        offsetPlane.Name = namePrefix & "_Plane"

        Dim hybridBody1 As HybridBody
        On Error Resume Next
        Set hybridBody1 = part.HybridBodies.Item("Construction")
        On Error GoTo 0
        If hybridBody1 Is Nothing Then
            Set hybridBody1 = part.HybridBodies.Add()
            hybridBody1.Name = "Construction"
        End If
        hybridBody1.AppendHybridShape offsetPlane

        Set refPlane = part.CreateReferenceFromObject(offsetPlane)
    End If

    ' Create sketch
    Set sketches = body.Sketches
    Set sketch = sketches.Add(refPlane)
    sketch.Name = namePrefix & "_Sketch"

    Set factory2D = sketch.OpenEdition()

    ' Create outer and inner circles (annulus profile)
    Set outerCircle = factory2D.CreateClosedCircle(x, y, outerDiameter / 2)
    Set innerCircle = factory2D.CreateClosedCircle(x, y, innerDiameter / 2)

    sketch.CloseEdition

    ' Create pad
    Set pad = shapeFactory.AddNewPad(sketch, height)
    pad.Name = namePrefix & "_Cylinder"
    pad.FirstLimit.Dimension.Value = height
End Sub
