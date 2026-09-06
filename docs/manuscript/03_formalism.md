# Formalism

::: {.definition #def:growth-record title="Growth record"}
A **growth record** $g = (id, title, wire, T_g, M_g, k)$ pairs an identifier
with a tag set $T_g$ over the reviewed vocabulary and an ordered tuple of
required markers $M_g$, grouped into a growth family $k$.
:::

::: {.definition #def:tag-vocabulary title="Tag vocabulary"}
The reviewed tag vocabulary $\mathcal{T}$ is a finite set of tag strings;
every record's tags must be drawn from it.
:::

::: {.definition #def:attempt title="Cultivation attempt"}
A **cultivation attempt** $a = (d, T_a, O, D)$ carries a description $d$, a
tag set $T_a$, an undated observation set $O$, and dated observations $D$
with ISO dates.
:::

::: {.definition #def:applicability title="Applicability"}
A record $g$ applies to an attempt $a$ exactly when $T_g \cap T_a \neq \emptyset$.
:::

::: {.definition #def:freshness title="Freshness"}
Given a review date $r$ and window $w$, an observation dated $t$ is **fresh**
if $t \le r$ and $r - t \le w$; **stale** if $t \le r$ and $r - t > w$;
**not counted** otherwise. Undated observations are fresh.
:::

::: {.definition #def:finding-rule title="Finding rule"}
For an applied record with marker surfaces (present $P$, missing $M$, stale
$S \subseteq M$): the status is STAGED when $M = \emptyset$; NEEDS_MARKER
when nothing was declared or $S = M$; NEEDS_REWORK otherwise.
:::

::: {.definition #def:aggregation title="Aggregation"}
The overall status is NEEDS_REWORK if any finding is NEEDS_REWORK; else
NEEDS_MARKER if any is NEEDS_MARKER; else STAGED if any finding exists; else
OUTSIDE_SCOPE.
:::

::: {.definition #def:counter-signal title="Counter-signal staging"}
An observation whose label matches the counter-signal phrase list is staged
aside with an intake note and contributes to no surface.
:::

::: {.proposition #prop:fail-closed title="Fail-closed registry"}
If the registry fails its shape check, the read is NEEDS_REWORK with no
findings and an intake note naming the defect.
:::

::: {.proposition #prop:empty-scope title="Empty scan set"}
If no record's tags intersect the attempt's tags, the read is OUTSIDE_SCOPE.
:::

::: {.proposition #prop:determinism title="Determinism"}
Two reads of the same attempt against the same registry at the same review
date produce identical canonical serializations and identical digests.
:::
