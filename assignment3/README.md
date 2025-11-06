Setup:

Using MESA Framework to create agent model

Agent class (mesa.Agent class):
    - Attributes:
        - unique id
        - model (reference to the STA model)
        - position
        - speed
        - communication range
        - protocol (which logic to follow)
        - active state (See below)
    - State Machine:
        Each state implements the respective logic and agent behaviour.
        - Searching State:
            Standard state, movement according to some logic (e.g. random) in search for tasks
        - Waiting for Help State:
            Agent has called for help and waits for it to arrive
        - Helping State:
            On the way to the agent who has been calling for help
        - Working State:
            Solving the given task

Task class:
    not a mesa object, simple implementation without actions, just to keep track of task states
    - Idle State -> after spawn, is existing somewhere and nothing happening
    - InProgress State -> Task is assigned and being worked on
    - Completed State -> Task is done and gets removed from the game

Task Manager:
    - has to ensure that always T number of tasks are present in the game