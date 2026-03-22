Sub CATMain()
    ' =====================================================
    ' ImportGearbox_v17 for 3DEXPERIENCE (Two-Phase)
    '
    ' Phase 1: Create ALL profiles first
    ' Phase 2: Create ALL lofts after
    '
    ' v17 Gearset:
    '   - Ring: 48 teeth, 80mm diameter
    '   - Planet: 18 teeth x 3
    '   - Sun: 12 teeth
    '   - Thickness: 22mm
    '   - Ratio: 5:1
    '   - Profile offset: -0.05mm (tooth thinning)
    '   - Ring compensation: 0.2 degrees
    ' =====================================================

    On Error Resume Next

    Dim editor As Object
    Dim part As Part
    Dim hsFactory As HybridShapeFactory
    Dim shpFactory As ShapeFactory

    Set editor = CATIA.ActiveEditor
    If editor Is Nothing Then
        MsgBox "No active editor. Please open a Part.", vbExclamation
        Exit Sub
    End If

    Set part = editor.ActiveObject
    If part Is Nothing Then
        MsgBox "No active Part found.", vbExclamation
        Exit Sub
    End If

    Set hsFactory = part.HybridShapeFactory
    Set shpFactory = part.ShapeFactory

    ' === CONFIGURATION - UPDATE THIS PATH ===
    Dim basePath As String
    basePath = "C:\YOUR_PATH_HERE\output_herringbone_v17\"

    Dim zLevels(2) As String
    zLevels(0) = "z_neg"
    zLevels(1) = "z0"
    zLevels(2) = "z_pos"

    Dim bodies As HybridBodies
    Set bodies = part.HybridBodies

    ' Storage for all spline references (5 gears x 3 levels = 15 splines)
    Dim allSplineRefs(4, 2) As Reference
    Dim gearNames(4) As String
    gearNames(0) = "sun_12"
    gearNames(1) = "planet_18_0"
    gearNames(2) = "planet_18_1"
    gearNames(3) = "planet_18_2"
    gearNames(4) = "ring_48"

    ' =========================================================
    ' PHASE 1: CREATE ALL PROFILES
    ' =========================================================
    MsgBox "Phase 1: Creating all profiles..." & vbCrLf & _
           "This may take a moment.", vbInformation, "Starting"

    Dim gearIdx As Integer
    For gearIdx = 0 To 4
        Call CreateProfiles(part, hsFactory, bodies, basePath, gearNames(gearIdx), zLevels, allSplineRefs, gearIdx)
    Next gearIdx

    part.Update

    MsgBox "Phase 1 Complete!" & vbCrLf & vbCrLf & _
           "All profiles created for:" & vbCrLf & _
           "  - Sun (12 teeth)" & vbCrLf & _
           "  - Planet 0, 1, 2 (18 teeth each)" & vbCrLf & _
           "  - Ring (48 teeth)" & vbCrLf & vbCrLf & _
           "Click OK to create lofts (Phase 2)", vbInformation, "Phase 1 Done"

    ' =========================================================
    ' PHASE 2: CREATE ALL LOFTS
    ' =========================================================
    For gearIdx = 0 To 4
        Call CreateLoft(part, shpFactory, gearNames(gearIdx), allSplineRefs, gearIdx)
    Next gearIdx

    part.Update

    MsgBox "v17 Gearbox Complete!" & vbCrLf & vbCrLf & _
           "Specs:" & vbCrLf & _
           "  - Ring: 48T, 80mm dia" & vbCrLf & _
           "  - Planets: 18T x 3" & vbCrLf & _
           "  - Sun: 12T" & vbCrLf & _
           "  - Thickness: 22mm" & vbCrLf & _
           "  - Ratio: 5:1" & vbCrLf & vbCrLf & _
           "If any loft shows error:" & vbCrLf & _
           "  1. Double-click the loft" & vbCrLf & _
           "  2. Check Closing Points" & vbCrLf & _
           "  3. Re-select to align them", _
           vbInformation, "Done!"

End Sub

Sub CreateProfiles(part As Part, hsFactory As HybridShapeFactory, bodies As HybridBodies, _
                   basePath As String, gearName As String, zLevels() As String, _
                   ByRef allSplineRefs() As Reference, gearIdx As Integer)

    On Error Resume Next

    ' Create Geometrical Set for this gear
    Dim geoSet As HybridBody
    Set geoSet = bodies.Add()
    geoSet.Name = gearName & "_Profiles"

    Dim level As Integer
    For level = 0 To 2
        Dim filePath As String
        filePath = basePath & gearName & "_" & zLevels(level) & ".txt"

        Dim fileNum As Integer
        Dim lineText As String
        Dim coords() As String
        Dim x As Double, y As Double, z As Double
        Dim pointCount As Integer

        fileNum = FreeFile
        Open filePath For Input As #fileNum

        pointCount = 0
        Dim ptArray() As HybridShapePointCoord
        ReDim ptArray(5000)

        Do While Not EOF(fileNum)
            Line Input #fileNum, lineText
            lineText = Trim(lineText)

            If Len(lineText) > 0 Then
                coords = Split(lineText, " ")

                If UBound(coords) >= 2 Then
                    x = CDbl(coords(0))
                    y = CDbl(coords(1))
                    z = CDbl(coords(2))

                    Dim pt As HybridShapePointCoord
                    Set pt = hsFactory.AddNewPointCoord(x, y, z)
                    geoSet.AppendHybridShape pt

                    Set ptArray(pointCount) = pt
                    pointCount = pointCount + 1
                End If
            End If
        Loop

        Close #fileNum

        ' Create spline
        If pointCount > 1 Then
            Dim spline As HybridShapeSpline
            Set spline = hsFactory.AddNewSpline()
            spline.Name = gearName & "_" & zLevels(level)

            Dim i As Integer
            For i = 0 To pointCount - 1
                Dim ref As Reference
                Set ref = part.CreateReferenceFromObject(ptArray(i))
                spline.AddPoint ref
            Next i

            spline.Closure = True
            geoSet.AppendHybridShape spline

            ' Store reference for Phase 2
            Set allSplineRefs(gearIdx, level) = part.CreateReferenceFromObject(spline)
        End If

        ReDim ptArray(5000)
    Next level

End Sub

Sub CreateLoft(part As Part, shpFactory As ShapeFactory, gearName As String, _
               ByRef allSplineRefs() As Reference, gearIdx As Integer)

    On Error Resume Next

    Dim loft As Loft
    Set loft = shpFactory.AddNewLoft()
    loft.Name = gearName & "_Solid"

    ' Add sections: z_neg -> z0 -> z_pos
    loft.AddSectionToLoft allSplineRefs(gearIdx, 0), 1, Nothing
    loft.AddSectionToLoft allSplineRefs(gearIdx, 1), 1, Nothing
    loft.AddSectionToLoft allSplineRefs(gearIdx, 2), 1, Nothing

    loft.SectionCoupling = 1
    loft.Relimitation = 1

    ' Add to PartBody
    Dim partBody As Body
    Set partBody = part.MainBody
    partBody.InsertHybridShape loft

End Sub
