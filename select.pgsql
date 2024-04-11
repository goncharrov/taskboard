select
    taskmembers.id,
    taskmembers.task_id
FROM
    task_task_members taskmembers,
    task_task tasks
WHERE
    taskmembers.task_id = 10
    AND taskmembers.user_id = 2
GROUP by
    taskmembers.id,
    taskmembers.task_id
    