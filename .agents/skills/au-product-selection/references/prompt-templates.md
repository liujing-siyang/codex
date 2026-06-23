# Prompt Templates

## Keyword Trend Validation

```text
Evaluate the keyword trend for this AU migration product candidate.
Candidate: {candidate}
Primary keyword: {primary_keyword}
Long-tail keywords: {long_tail_keywords}
Trend data: {keyword_history}
Sources: {source_refs}

Tasks:
1. Calculate or verify 3/6/12-month growth rates.
2. Decide whether each keyword is rising, flat, falling, or insufficient.
3. Rank long-tail keywords by growth rate first, not by absolute search volume.
4. If growth is not rising, do not recommend 优先进入.
```

## VOC And Social Mining

```text
Analyze consumer pain points and desire signals for this candidate. Group findings by pain-point dimension. Provide frequency if countable, affected product type, product improvement direction, and whether the insight is transferable to AU consumers.
```

## AU Migration Fit

```text
Assess whether this source-market product opportunity can migrate to Amazon AU. Evaluate cultural fit, shopping habit similarity, seasonality, AU competitor gap, compliance/regulatory issues, import risk, and beginner-seller testability.
```

## Patent And Compliance Rough Screen

```text
Perform a rough patent and compliance risk screen. Do not declare the product safe. Identify obvious red flags and recommend manual checks.
```
