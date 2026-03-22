# CATIA Skeleton Documentation — Discussion Document

**Purpose:** Capture your knowledge about the QDD CATIA skeleton assembly before it gets lost. Fill this in at your own pace — short answers, bullet points, or stream-of-consciousness all work. We'll compile this into a cleaner baseline doc afterward.

**How to use:** Replace the `> **Your thoughts:**` sections with your answers. Paste screenshots inline where it helps (VS Code supports `![](path)` or just drag-drop).

---

## 1. Assembly Structure

### What's the top-level structure?
*How does it organize? Skeleton → parts → assemblies? Or something else?*

> **Your thoughts:**
> 
>
> *(e.g., "Top level is the main assembly, skeleton is a subcomponent, then each stage sits under that...")*

### What controls what?
*Which elements drive others? What's upstream vs downstream?*

> **Your thoughts:**
>

### Hierarchy diagram
*If you have a mental map of how it's organized, sketch it or describe it here.*

> **Your thoughts:**
>
> ```
> (paste ASCII diagram or describe structure)
> ```

**Screenshot placeholder:** *If you can grab a tree view from CATIA showing the assembly structure, paste here.*

---

## 2. Key Variables/Parameters

### What are the main variables that control the design?
*The parameters you actually change when iterating.*

> **Your thoughts:**
>
> | Variable | What it controls |
> |----------|------------------|
> |          |                  |
> |          |                  |

### What happens when you change each one?
*Quick description of the ripple effects.*

> **Your thoughts:**
>

### Are there dependencies?
*Changing X forces Y to change? Any linked parameters?*

> **Your thoughts:**
>

---

## 3. Origin & Constraint Philosophy

### How is the assembly fixed? Where's the master origin?
*What's grounded? What defines "center" of the actuator?*

> **Your thoughts:**
>

### How are parts constrained to each other?
*Coincident faces? Offset planes? Mate constraints?*

> **Your thoughts:**
>

### Any "golden rules" you follow for constraints?
*Things you always do or never do.*

> **Your thoughts:**
>
> - [ ] Always constrain to skeleton, never part-to-part
> - [ ] Use offset constraints instead of coincident for adjustability
> - [ ] Other:

---

## 4. Skeleton Specifics

### What does the 3D skeleton actually control?
*What geometry lives in the skeleton? Planes, axes, points, curves?*

> **Your thoughts:**
>

### What's the relationship between skeleton geometry and actual parts?
*How do parts "read" from the skeleton?*

> **Your thoughts:**
>

### What would break if you modified the skeleton?
*The scary parts — what's fragile?*

> **Your thoughts:**
>

**Screenshot placeholder:** *A view of the skeleton geometry would be helpful here.*

---

## 5. Things That Bit You

### Any modeling mistakes you had to undo?
*Decisions that seemed fine but caused problems later.*

> **Your thoughts:**
>

### Parts that are fragile or break easily when changed?
*The "don't touch this" zones.*

> **Your thoughts:**
>

### Lessons learned about CATIA specifically?
*Quirks, workarounds, things you'd tell past-you.*

> **Your thoughts:**
>

---

## 6. What's Not Obvious

### If your collaborator opened this tomorrow, what would confuse them?
*Things that aren't self-documenting.*

> **Your thoughts:**
>

### Any hidden dependencies or non-obvious connections?
*Things that aren't visible in the tree but matter.*

> **Your thoughts:**
>

---

## Quick Hits (Optional)

Anything else that comes to mind:

- [ ] Naming conventions you use
- [ ] File organization on disk (where do parts live?)
- [ ] Version control approach (if any)
- [ ] External references or links between files
- [ ] Other:

> **Additional notes:**
>

---

## Next Steps
Once you've filled this in (doesn't have to be complete):
1. We review together
2. Compile into a cleaner `catia-skeleton.md` baseline doc
3. Future changes get captured via `/doc` workflow
