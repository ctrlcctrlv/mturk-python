mturk-python
============

Complete Mechanical Turk API written in Python that uses the same names as the official documentation

mturk.py is a small library that sends requests to Mechanical Turk. It is much simpler than other libraries which redefine every function that Mechanical Turk recognizes. This saves you time so you don't have to worry about the library, just the Mechanical Turk API.

Read the official mTurk API docs [here](http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/Welcome.html).

**Your configuration file, passed as a dict to MechanicalTurk or saved in mturkconfig.json**

`stdout_log` enables the requests log of each request made to mTurk. `verify_mturk_ssl` verifies mTurk's SSL certificate. This should be left `true` in most cases, but according to bug reports it's broken on some operating systems.

```json
{
"use_sandbox" : false,
"stdout_log" : false,
"verify_mturk_ssl" : true,
"aws_key" : "ACCESSID",
"aws_secret_key" : "PASSWORD"
}
```
**Getting your balance**
```python
import mturk
m = mturk.MechanicalTurk()
r = m.request("GetAccountBalance")
if r.valid:
    print r.get_response_element("AvailableBalance")
```
**Assigning a qualification**
```python
import mturk
m = mturk.MechanicalTurk()
workers = ["A1ZZZ","A1QQQ"] # Replace these, of course!
for worker in workers:
    m.request("AssignQualification",
                {"QualificationTypeId":"2MYQUALIFICATION",
                 "WorkerId":worker, "IntegerValue":100})
```
If you find any bugs please open a new issue. 
