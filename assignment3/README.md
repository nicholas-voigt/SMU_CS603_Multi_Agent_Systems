PyGame Setup:

Agent class:
    - Searching State -> randomly running around to find the next task
    - Calling Help State -> If task was found, but there are not enough agents to do it. Emitted call for help and waits for response (maybe needs a kill time or a way to retract the call and join other calls)
    - Helping State -> Heard a help call from another agent and is moving in to help
    - Working State -> Working on solving the current task

Task class:
    - Idle State -> after spawn, is existing somewhere and nothing happening
    - InProgress State -> Task is assigned and being worked on
    - Completed State -> Task is done and gets removed from the game

Task Manager:
    - has to ensure that always T number of tasks are present in the game