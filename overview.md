# Message overview

## overview

- create_RAT
- fetch_RATs
- available_RATs
- start_RAT
- start_iRAT
- student_iRAT_done
- iRAT_done
- start_tRAT
- tRAT_answers
- tRAT_done
- timer_expired

## 1. create_RAT

Command: "create_RAT"\
Sender: Teacher\
Receiver: Server\
Channel: "ttm4115/team_5/teacher"\
Function: Sends a message to the server with a RAT that is to be stored in the database\
JSON format:

```json
{
  "command": "create_RAT",
  "RAT": {
    "id": "5397c02f-3572-42c4-b861-4f6cfb891186",
    "name": "TestRAT",
    "size": 2.0,
    "subject": "TTM4115",
    "questions": {
      "1": {
        "question": "TestQ1",
        "correct": "correct",
        "a": "fail1",
        "b": "fail2",
        "c": "fail1"
      },
      "2": {
        "question": "TestQ2",
        "correct": "correct",
        "a": "fail1",
        "b": "fail2",
        "c": "fail3"
      }
    }
  }
}
```

## 2. fetch_RATs

Command: "fetch_RATs"\
Sender: Teacher\
Receiver: Server\
Channel: "ttm4115/team_5/teacher"\
Function: Requests an overview of the RATs in the database\
JSON format:

```json
{
  "command": "fetch_RATs"
}
```

## 3. available_RATs

Command: "available_RATs"\
Sender: Server\
Receiver: Teacher\
Channel: "ttm4115/team_5/teacher"\
Function: Sends an overview of the RATs in the database\
JSON format:

```json
{
  "command": "available_RATs",
  "rat_info": {
    "75e60adc-e830-11ed-a05b-0242ac120003": "RAT_1",
    "8b07615d-fa1c-4e39-95f5-caddde20b113": "RAT_2",
    "3c087784-ca0c-4922-8642-a78b4fe06666": "RAT_3",
    "ca654113-c46c-4b94-98ed-b2af060d24c8": "RAT_4",
    "f0c0794d-0eaf-4937-b85b-7f46495e9040": "RAT_5"
  }
}
```

## 4. start_RAT

Command: "start_RAT"\
Sender: Teacher\
Receiver: Server\
Channel: "ttm4115/team_5/teacher"\
Function: Tells the server to start a RAT session.\
JSON format:

```json
{
  "command": "start_RAT",
  "RAT_ID": "75e60adc-e830-11ed-a05b-0242ac120003"
}
```

## 5. start_iRAT

Command: "start_iRAT"\
Sender: Server\
Receiver: Student\
Channel: "ttm4115/team_5/student"\
Function: After "start_RAT" has been sent from the Teacher, the server sends the RAT to the students, and starts a timer. \
JSON format:

```json
{
  "command": "start_iRAT",
  "RAT": {
    "1": {
      "question": "What is the capital city of Norway?",
      "correct": "Oslo",
      "a": "Stockholm",
      "b": "Copenhagen",
      "c": "Helsinki"
    },
    "2": {
      "question": "What is the largest organ in the human body?",
      "correct": "Skin",
      "a": "Heart",
      "b": "Lung",
      "c": "Liver"
    },
    "3": {
      "question": "What is the tallest mountain in the world?",
      "correct": "Mount Everest",
      "a": "Mount Kilimanjaro",
      "b": "Mount McKinley",
      "c": "Mount Aconcagua"
    }
  }
}
```

## 6. student_iRAT_done

Command: "student_iRAT_done"\
Sender: Student\
Receiver: Server\
Channel: "ttm4115/team_5/student"\
Function: Tells the server that a student is done with their iRAT, and the questions that was correct\
JSON format:

```json
{
   "command":"student_iRAT_done",
   "student_ID": "1"
   "team_ID": "1"
   "RAT_ID": "75e60adc-e830-11ed-a05b-0242ac120003"
   "answers": "[correct, a, correct]"
}
```

## 7. iRAT_done

Command: "iRAT_done"\
Sender: Server\
Receiver: Server\*\
Channel: "ttm4115/team_5/server"\
Function: Tells the server that an entire team of students are done with their iRAT\
JSON format:

```json
{
   "command":"iRAT_done",
   "team_ID": "1"
   "RAT_ID": "75e60adc-e830-11ed-a05b-0242ac120003"
   "answers": "[correct, a, correct]"
}
```

## 8. start_tRAT

Command: "start_tRAT"\
Sender: Server\
Receiver: Student\
Channel: "ttm4115/team_5/student"\
Function: Starts the tRAT and chooses a team leader after the entire team is done with the iRAT\
JSON format:

```json
{
   "command":"start_tRAT",
   "team_ID": "1"
   "leader_ID": "1"
}
```

## 9. tRAT_answers

Command: "start_tRAT"\
Sender: Student\
Receiver: Server\
Channel: "ttm4115/team_5/student"\
Function: Sends the tRAT answers to the server,\
JSON format:

```json
{
  "command": "tRAT_answers",
  "RAT_id": "1",
  "team_id": "1",
  "answers": "[correct, correct, correct]"
}
```

## 10. tRAT_done

Command: "tRAT_done"\
Sender: Server\
Receiver: Server\*\
Channel: "ttm4115/team_5/teacher"\
Function: Tells the server that a team is done with the tRAT.\
JSON format:

```json
{
  "command": "tRAT_done"
}
```

## 11. timer_expired

Command: "_x_\_expired"\*\*\
Sender: Server\
Receiver: Student\
Channel: "ttm4115/team_5/student"\
Function: Tells a student during the iRAT or the student leader during a tRAT that the RAT timer has expired, forcing the student to submit their answers\
JSON format:

```json
{
  "command": "x_expired"
}
```

## Footnotes

\* The team manager sends an mqtt message to the manager. We did this to allow for there to be different servers operating at the same time, but we implemented everything on the same server

\*\* The "x" is the name of the timer. If we start timer "t1" at the iRAT, the command will be: "t1_expired".
