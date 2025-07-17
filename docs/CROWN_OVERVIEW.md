# Crown Agent Overview

The diagram below shows how the main components interact when using the console.

```
+--------------------+
|    Crown Console   |
+---------+----------+
          |
          v
+---------+----------+
|   Crown Agent      |
| (GLMIntegration)   |
+---------+----------+
          |
          v
+---------+----------+
| State Transition   |
| Engine             |
+---------+----------+
          |
     +----+----+
     |         |
     v         v
+--------+ +---------------+
|  GLM   | | Servant Models|
| 4.1V   | | (DeepSeek etc)|
+--------+ +---------------+
```

User commands enter through the **Crown Console**. The **Crown Agent** sends
requests to the GLM service and keeps recent history in memory. The
**State Transition Engine** tracks ritual phrases and emotional cues. It may
delegate a prompt to one of the registered servant models when appropriate.
