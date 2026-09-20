# discord-backroom-TRPG-bot
---
## Contents
1. command (slash)
2. database
---
## 1. command
### /roll
- Argument : /roll (expression)
- expression form
    - operator : +, -
    - (number_of_repetitions)d(number) -> random 1 ~ (number) for number_of_repetition
    - only number : (number)
- return total result
### /레벨변경
- Argument : /레벨변경 (number)
- save (number) to the database (Defualt : 레벨 없음)
### /레벨조회
- Argument : /레벨조회
- querying data from database (Default : 레벨 없음)
### /랜덤레벨
- Argument : /랜덤레벨
- save random level (0 ~ 999) to the database
---
## database
| user's discord id | level |
