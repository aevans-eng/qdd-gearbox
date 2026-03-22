' ============================================================
' Skeleton to Cylinders - Creates solids from skeleton geometry
' ============================================================
' Run AFTER PlanetarySkeletonTrue.bas
' Creates padded cylinders referencing the skeleton circles
' ============================================================

Sub CATMain()

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

    ' Find the Skeleton geometrical set
    Dim skeleton As HybridBody
    On Error Resume Next
    Set skeleton = part.HybridBodies.Item("Skeleton")
    On Error GoTo 0

    If skeleton Is Nothing Then
        MsgBox "No 'Skeleton' geometrical set found." & vbCrLf & _
               "Run PlanetarySkeletonTrue.bas first.", vbExclamation
        Exit Sub
    End If

    ' === DIMENSIONS ===
    Dim FaceWidth As Double: FaceWidth = 10

    Dim shapeFactory As ShapeFactory
    Set shapeFactory = part.ShapeFactory

    Dim bodies As Bodies
    Set bodies = part.Bodies

    Dim refPlaneXY As Reference
    Set refPlaneXY = part.CreateReferenceFromObject(part.OriginElements.PlaneXY)

    Dim body As Body
    Dim sketch As Sketch
    Dim factory2D As Factory2D
    Dim pad As Pad
    Dim refCircle As Reference
    Dim projCircle As Geometry2D

    ' === SUN GEAR ===
    Dim sunCircle As HybridShape
    Set sunCircle = skeleton.HybridShapes.Item("CIRCLE_PITCH_SUN")

    If Not sunCircle Is Nothing Then
        Set body = bodies.Add()
        body.Name = "Sun_Gear"

        Set sketch = body.Sketches.Add(refPlaneXY)
        sketch.Name = "Sun_Sketch"

        Set factory2D = sketch.OpenEdition()
        Set refCircle = part.CreateReferenceFromObject(sunCircle)
        Set projCircle = factory2D.CreateProjection(refCircle)
        sketch.CloseEdition

        Set pad = shapeFactory.AddNewPad(sketch, FaceWidth)
        pad.Name = "Sun_Pad"
    End If

    ' === PLANET GEARS ===
    Dim i As Integer
    Dim planetCircle As HybridShape

    For i = 1 To 3
        On Error Resume Next
        Set planetCircle = skeleton.HybridShapes.Item("CIRCLE_PITCH_PLANET_" & i)
        On Error GoTo 0

        If Not planetCircle Is Nothing Then
            Set body = bodies.Add()
            body.Name = "Planet_" & i

            Set sketch = body.Sketches.Add(refPlaneXY)
            sketch.Name = "Planet_" & i & "_Sketch"

            Set factory2D = sketch.OpenEdition()
            Set refCircle = part.CreateReferenceFromObject(planetCircle)
            Set projCircle = factory2D.CreateProjection(refCircle)
            sketch.CloseEdition

            Set pad = shapeFactory.AddNewPad(sketch, FaceWidth)
            pad.Name = "Planet_" & i & "_Pad"
        End If
    Next i

    ' === RING GEAR (hollow) ===
    Dim ringInner As HybridShape
    Dim ringOuter As HybridShape
    Dim refInner As Reference
    Dim refOuter As Reference

    Set ringInner = skeleton.HybridShapes.Item("CIRCLE_PITCH_RING")
    Set ringOuter = skeleton.HybridShapes.Item("CIRCLE_OUTER_RING")

    If Not ringInner Is Nothing And Not ringOuter Is Nothing Then
        Set body = bodies.Add()
        body.Name = "Ring_Gear"

        Set sketch = body.Sketches.Add(refPlaneXY)
        sketch.Name = "Ring_Sketch"

        Set factory2D = sketch.OpenEdition()
        Set refOuter = part.CreateReferenceFromObject(ringOuter)
        Set refInner = part.CreateReferenceFromObject(ringInner)
        Set projCircle = factory2D.CreateProjection(refOuter)
        Set projCircle = factory2D.CreateProjection(refInner)
        sketch.CloseEdition

        Set pad = shapeFactory.AddNewPad(sketch, FaceWidth)
        pad.Name = "Ring_Pad"
    End If

    part.Update

    MsgBox "Cylinders created from skeleton!", vbInformation

End Sub
