SELECT pr_number, score, z_score
FROM pr_events
ORDER BY z_score DESC
LIMIT 20;
