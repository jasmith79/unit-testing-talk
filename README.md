# Test You Some Code, For Great Justice!

This document will cover the why and how of unit testing your Python code, although much of it will be more broadly-applicable to writing software. Much like the git workflow tutorial this is overkill for really simple stuff, but also like the git workflows this is not an all-or-nothing proposition, the more of this you adopt the better off you'll be.

## What Kind of Testing Are We Talking About?

Code testing generally falls into one of three rough buckets:

1. *Unit tests* test a *single* unit of execution, usually one function or method.
2. *Integration tests* test the interaction of multiple units of execution, usually at the module or project level.
3. *End-to-end tests* test what it says on the tin: an entire *system*, ex spins up a database, a REST server, and a static asset server, scripted interaction with a webpage causes the thing to go through the REST server and end up in Postgres.

We will today be *only* talking about unit tests because they are by far the most important. In fact, some would go so far as to say that integration tests are a [scam and a lie](https://vimeo.com/80533536). Even if that's extreme, they are definitely a *crutch*, they are a symptom that your code is not amenable to the strictly superior unit testing.

End-to-end tests are actually extremely valuable but their implementation and tooling are vastly more complex, those will wait for another time.

## WIIFM (What's In It For Me?)

Testing is *work*. So what do you get for that work? Obviously verifying the thing does what you expect it to do is important, but you can check that in the terminal window in 10 seconds. That doesn't really hit the value propositions of *automating* the process. The single most important thing the kind of testing I'm advocating here buys you is actually *design feedback*. Consider the following Python function: 

```python
def some_fun(x):
    if is_valid(x):
        return x * 5
    else:
        logger.log("Invalid input to x")
```

At first glance this isn't so so bad, but... it fails some basic quality-of-design questions: can I move it? Can I split it? Can I check the return value? Is the input/output contract well-defined?

```python
def some_fun(x):     # WTF does 'some_fun' mean? WTF is x?
    if is_valid(x):  # implicit dependency on is_valid being in enclosing scope
        return x * 5 # int or float or even list? does it matter?
    else:
        logger.log("Invalid input to some_fun") # implicit dependency on logger
        # implicitly returns None, not a number type!
```

Now, certainly, an experienced programmer can glance at something like this and see the potential problems in this trivial example. But if it's a more complicated function, or the programmer is not so experienced, or both, then testing is a great way to find out all the potential problems in the design. More on this example a bit later.

The second most important thing that tests buy you is *catching regressions*. A regression is when you fix a bug, and then make a different code change later that reintroduces it. Consider the following function that calculates a subnet mask from a CIDR number:

```python
def calc_subnet_mask(cidr_number):
    """Calculates the correct submask from the given number in CIDR notation"""
    
    bit_string = ("1" * cidr_number).ljust(32, "0") # pad CIDR number of 1's with 0's to 32 bit
    byte_strings = [bit_string[i:i + 8] for i in range(0, len(bit_string), 8)] # segment into 4 8bit bytes
    byte_list = [str(int(y, 2)) for y in byte_strings] # convert the 4 bytes to decimal notation
    return ".".join(byte_list) # join as a string with a '.'
```

This function has a deliberate bug. Without peeking ahead, can you spot it?

....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................
....................................................................................................

Here's a hint: what happens if you pass this a negative number? Greater than 32? Floating point value? Null? Let's fix that:

```python
def calc_subnet_mask(cidr_number: int) -> str: # type annotation prevents float, None, etc
    """Calculates the correct submask from the given number in CIDR notation"""
    if not 0 <= cidr_number <= 32: # checking if value is in expected range
        raise ValueError(
            "CIDR values are between 0 and 32 inclusive, received {}".format(
                str(cidr_number),
            )
        )

    bit_string = ("1" * cidr_number).ljust(32, "0")
    byte_strings = [bit_string[i:i + 8] for i in range(0, len(bit_string), 8)]
    byte_list = [str(int(y, 2)) for y in byte_strings]
    return ".".join(byte_list)
```

That *should* fix the problems but let's add some tests to make sure. Don't worry about syntax for now:

```python
import pytest

from nethelper import calc_subnet_mask

class TestCalcSubnetMask:
    """Tests the calc_subnet_mask function"""

    def test_zero(self):
        assert calc_subnet_mask(0) == "0.0.0.0"
    
    def test_32(self):
        assert calc_subnet_mask(32) == "255.255.255.255"
    
    def test_16(self):
        assert calc_subnet_mask(16) == "255.255.0.0"
    
    def test_negative(self):
        with pytest.raises(ValueError, match="CIDR values are between 0 and 32 inclusive"):
            calc_subnet_mask(-5)
    
    def test_too_high(self):
        with pytest.raises(ValueError, match="CIDR values are between 0 and 32 inclusive"):
            calc_subnet_mask(50)
```

Then to run them:

## Running the Tests

Let's try out the tests we just wrote: run `pytest tests/nethelper.py` and verify they work. We'll cover what that just did in a minute.

I didn't write tests for floats, None, and other completely invalid inputs, I'm relying on the type annotations and static analysis to do that for me here, but you could easily add tests for those too. Now we've fixed the bug! But later on careless Joe the programmer realizes that there is problem with a boundary condition in a different numeric check somewhere else in the same file and because he's a lazy sort of fellow he ctrl-f's and replaces every 32 in the file with 33. Now an invalid CIDR of 33 will slip through, and the bug that you already spent time fixing is now reintroduced... unless you have the tests to catch it!

The third important thing tests buy you is *communication with other people* (including you 6 months from now). Much like comments, except tests are **waaay better**: the machine can run them and tell you when they no longer match the code they are describing, which isn't true at all of comments. Tests (if well written) describe inputs and outputs, the API contract, boundary cases, what exceptions are expected, etc.

The fourth thing that this type of testing buys you is sleep. On every project there's an elephant in the room that grows in size throughout the lifecycle, and that elephant is *the code you've already written*. Every one of us is Dr. Frankenstein, and we've created monsters. If your code isn't isolated (ensured by the tests) you will be straight up scared to modify it for fear of silently breaking it. With tests, you know that a) changes in foo shouldn't affect bar and b) even if by some weird happenstance it does the tests should catch it.

## Ok, So How Now?

Alright, tests are awesomesauce, we get it, how do we get there?

Python's standard library has facilities for unit testing. They're... ok, but pytest is just better. The API is less clunky, the output better formatted, etc. You can install pytest with pip, and unlike most things where you'd want to use venv it's probably ok to install globally on your system.

You can use pytest like so:

```bash
pytest # runs all tests in $CWD, equivalent to pytest ./*.py
pytest some_dir/*.py # run all tests in some_dir
pytest tests/some_test.py # run all tests in some_test file
```

Let's start at the very beginning (a very good place to start). Project layout, from [realpython](https://realpython.com/python-application-layouts/#command-line-application-layouts):

```
helloworld/
│
├── helloworld/
│   ├── __init__.py
│   ├── helloworld.py
│   └── helpers.py
│
├── tests/
│   ├── helloworld_tests.py
│   └── helpers_tests.py
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py
```

You can see an actual sample repo with this kind of structure [here](https://github.com/graingert/samplemod), and this repo itself is pretty similar.

So lets bring back our less-than-stellar function from the beginning:

```python
def some_fun(x):
    if is_valid(x):
        return x * 5
    else:
        logger.log("Invalid input to x")
```

And let's think about how we'd test this thing. Here are some questions I ask when writing a test:

* What are the *semantics* of this function? What is it supposed to *do*?
* What are the possible [side-effects](https://en.wikipedia.org/wiki/Side_effect_(computer_science)#:~:text=In%20computer%20science%2C%20an%20operation,the%20invoker%20of%20the%20operation.) (I/O, thrown exceptions, etc) of this function?
* What *context* is required for this thing to work? What implicit/explicit dependencies?
* What are some expected input and output values (i.e. the happy path)?
* What are some known boundary conditions?

Right off the bat, by asking these questions we start to see some of the problems I outlined. For the first question, `some_fun`, `x`, and `is_valid` are completely generic names that offer no insight into what the function is supposed to accomplish. I ask the semantics question first because it's the most important: it guides our intuitive understanding of what things are for. Don't mess with the semantics or you'll find your self in a situation where yesterday `draw()` drew pictures, but today it draws guns. Contrast this with the other example above `calc_subnet_mask(cidr_number: int) -> str` is pretty clear on the tin about the intention.

For the second question, there is definitely an obvious side-effect here in that it will log an invalid input, but there are also some potential hidden ones:

```python
def some_fun(x):
    if is_valid(x): # can is_valid throw? Does *it* do any I/O?
        return x * 5 # throws if x is not valid for multiplication
    else:
        logger.log("Invalid input to x") # the obvious one
```

For the third question, this function has one explict dependency (the parameter x, about which we know of no constraints because of the above-mentioned semantic issues) and two implicit dependencies: `is_valid` and `logger`. **Implicit dependencies are a huge impediment to writing good tests (and by extension good *code*) and should be minimized or eradicated.** More on that in a bit.

For the fourth question we can infer from the implementation that if we give it a number we should get back the same number multiplied by 5, but again there's that `is_valid` check we have to reckon with. We can also expect to get back `None` if the check fails.

For question five we have no clue, we'll have to read the implementation of `is_valid` to figure it out.

Let's say for the purpose of this demo though that we looked at `is_valid` and x can be any positive integer less than the MAX_INT, and that the `is_valid` function cannot throw an error and doesn't do any I/O. **NOTE: although the tests we're are about to write will document some of the edge cases much of this information is still propagated *implicity* through the system. Any change in the `is_valid` function can break all these or render them meaningless** The proper, *isolated* test for this function, as written, looks like this:

```python
import os
import sys

# We need to do this because otherwise the test dir won't
# have our local files to import on path. Normally I (and
# a lot of other people) abstract this out with a file usually
# called something like "context" so we don't have to repeat
# this in every single test file (see the other examples)
# but here we have to in order to be able to monkeypatch
# the closure vars.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import math
from unittest import mock
import pytest
from some_module import some_module


class TestSomeFun:
    def test_zero(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(0)
        is_valid.assert_called_with(0)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_negative(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(-3)
        is_valid.assert_called_with(-3)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_infinity(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=False)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(math.inf)
        is_valid.assert_called_with(math.inf)
        logger.log.assert_called_with("Invalid input to x")
        assert result is None

    def test_positive_int(self, monkeypatch):
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        is_valid = mock.MagicMock(return_value=True)
        monkeypatch.setattr(some_module, "logger", logger)
        monkeypatch.setattr(some_module, "is_valid", is_valid)
        result =  some_module.some_fun(5)
        is_valid.assert_called_with(5)
        logger.log.assert_not_called()
        assert result == 25
```

and then run them:

`pytest tests/less_good.py`

Yikes. They *work*, but that's a LOT of verbiage and patching and syntax for a function with < 10 LoC. Note that we have multiple mocks and patches *per test*. This is the kind of thing I meant when I said testing gives you feedback on your design.
    
So let's re-write this to separate the concerns and be more amenable to this sort of testing:

```python
from functools import partial

def is_valid(n):
    return isinstance(n, (int, float)) and n > 0 and n != math.inf

def times_five(n):
    return n * 5

def not_quite_some_fun(logger, validator, xform, n):
    if validator(n):
        return xform(n)
    else:
        logger.log("Invalid input")

some_fun = partial(not_quite_some_fun, logger, is_valid, times_five)
```

Now the tests look like this:

```python
import math
from unittest import mock
import pytest

# Note we don't even care about some_fun itself anymore
from some_module import is_valid, not_quite_some_fun
        
class TestIsValid:
    def test_non_number(self):
        assert not is_valid(None)
        assert not is_valid([])
        assert not is_valid({})
        assert not is_valid("foo")
    
    def test_infinity(self):
        assert not is_valid(math.inf)
    
    def test_zero(self):
        assert not is_valid(0)
    
    def test_happy(self):
        assert is_valid(10)

# times_five is so trivial we won't even bother

class TestNQSF:
    def test_valid(self):
        validator = mock.MagicMock(return_value=True)
        xform = mock.MagicMock(return_value=3)
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        result = not_quite_some_fun(logger, validator, xform, 3)
        assert result == 3
        logger.log.assert_not_called()
        xform.assert_called_with(3)

    def test_invalid(self):
        validator = mock.MagicMock(return_value=False)
        xform = mock.MagicMock()
        logger = mock.MagicMock()
        logger.log = mock.MagicMock()
        result = not_quite_some_fun(logger, validator, xform, 3)
        logger.log.assert_called_with("Invalid input")
        xform.assert_not_called()
        assert result is None
```

Look ma, no monkey-patching. There are more tests because now we are explicitly and directly testing the logic of `is_valid`, but for the actual function there are just two paths with one test each..

And note too that the change is completely transparent to the caller of `some_fun`, they'll never know that it's a partially-applied version of a function that takes all of that context (e.g. `logger`, `is_valid`) as explicit parameters instead of closed-over variables. Now the validation logic is independent and independently testable of the transformation and logging logic. 

This isn't perfect. It still suffers from the semantic issues of not being very well-named. It still has an inconsistent return type (`int | float | None`). But it's light-years simpler to understand and test. Actually, lets talk about that 'simpler to understand' part for a second. Because it may not be clear at first glance that 

```python
def some_fun(x):
    if is_valid(x):
        return x * 5
    else:
        logger.log("Invalid input to x")
```

is harder to understand than this version:

```python
def not_quite_some_fun(logger, validator, xform, n):
    if validator(n):
        return xform(n)
    else:
        logger.log("Invalid input)

some_fun = partial(not_quite_some_fun, logger, is_valid, times_five)
```

I mean, the first version looks pretty short and sweet, parses nicely into an English sentence, etc. It's only once you start to write a rigorous specification of the behavior that you really start to see the inadequacies of the first approach. This same need for rigor is also the reason legal contracts are written in legalese instead of plain English. You start asking about what stuff means and what the failure modes and boundary conditions are, because that's the real-world meaning of "easy to understand" that we actually care about as engineers, not the "does it look deceptively simple at a glance" meaning.

So now that we have some reasonable tests, let's talk about what's going on in them.

```python
# Critical, pytest won't run files that don't import the package
import pytest

# Imports the stuff we want to test from our module.
from some_module import is_valid, not_quite_some_fun

# The class isn't strictly necessary but I use it as a mechanism to group
# related tests.
class TestIsValid: # no constructor, the meat is in the methods
    def test_non_number(self): # describes what the test is
        # assert the expected result, a lot of thes could be
        # omitted in favor of type annotations
        assert not is_valid(None)
        assert not is_valid([])
        assert not is_valid({})
        assert not is_valid("foo")
```

## Mocks

A mock is just a dummy value that you can use in place of a real one. Python provides very nice mocking facilities that allow you to specify, introspect on, and assert the type of their interactions. Note that when testing the logging etc. in our function we're providing a mock:

```python
from unittest import mock

import pytest

class TestNQSF:
    def test_valid(self):
        # We're mocking the validator to just return true
        validator = mock.MagicMock(return_value=True)
        xform = mock.MagicMock(return_value=3)
        logger = mock.MagicMock()
        logger.log = mock.MagicMock() # log method is what we care about
        result = not_quite_some_fun(logger, validator, xform, 3)
        assert result == 3
        validator.assert_called_with(3)
        logger.log.assert_not_called() # we could alternatively assert it got called
        xform.assert_called_with(3) # The function we're testing passed the expected arg
```

## The Rules of Test Club

In addition to the nuts and bolts of how to write pytest tests, there are some rules that fall out of good testing practice:

1. ~~You do not talk about Test Club~~ Tests should be *independent*.
2. ~~You do **not** talk about Test Club~~ Tests should be repeatable.
3. Tests should be simple.
4. Tests should be automated.
5. Tests should be heeded.

Any failure to follow these rules will result in code that is more brittle and less reliable.

### Tests Should Be *Independent* and *Repeatable*

The success or failure of tests should not depend on anything outside of the function being tested, and a test should never pass one time and fail another without the code being tested changing. You kind of have to excercize some judgement here. Lets say in our above example that the `is_valid` function is actually a third-party library function. You may not want to use a parameter and partial application in that case, library code changes much less often than your own. You'll still need to patch it out though, so your call.

The two biggest threats to the independence of tests are *closure* and *state*. The closure problem is more of a specific instance of the state problem but is common and fraught enought to deserve it's own mention. Closure is where a function *closes-over* a variable from an enclosing scope. For instance `some_fun` originally captured the `is_valid` and `logger` variables from an enclosing scope. This means that either the test of `some_fun` is going to depend on things outside the test (i.e. it's not a unit test because we're not testing a single unit of execution but the interaction of several) or you will have to monkey-patch out the variables from the enclosing scope (if your language even let's you, Python does) in which case [instead of testing the things you're testing mocks](https://destroyallsoftware/talks/boundaries). Not good.

In the revamped code and tests, there is no monkey patching. Everything depends *only* on it's arguments. There are no mocks in any of the logic tests so they run with *real inputs and dependencies*, we only use mocks to test the aggregating function `not_quite_some_fun` to make sure it wires stuff up the way we expect, and we pass them directly. Closures aren't necessarily *bad*, for instance they form the basis of the awesome partial application function from the functools module in the standard library. But they are *dependencies*, and you *must* think of them that way or they'll bite you in the rear.

It's easiest to explain state by talking about what it isn't. The contrast to state is a *constant*. Consider the following:

```python
MAX_THREADS = 5
users = []
```

Here it's pretty obvious that we've got a constant and a stateful mutable variable: `MAX_THREADS` is assigned a literal integer and follows the all caps convention for constants. While Python will let you reassign it, any of your tools (linter, static analyzer) are going to complain and any assingment to an all caps var that occurs somewhere other than the top of the file is going to stick out like a sore thumb in the code. The `users` list by contrast is *obviously* stateful, if we weren't going to mutate it later (to add the users) it would be superfluous: what good is an *empty* user list?

State is always a problem in tests, but the real problem comes when it bleeds into other contexts. **Any use of state should be explicit.** Prefer funargs over closures, plain data (list, tuple, dict, data class, etc) and functions over stateful objects. If you have 5 tests that depend on the global `users` list, the success of one test could depend on how the others went! In other words, not *repeatable* (see Rule #2). The same test should never fail one time and pass the next if the code hasn't changed.

### Tests Should be Simple

If a test fails and you don't *immediately* understand why, either the code or the test or both are too complex. Things that you will want to avoid in your tests:

* Logic expressions like conditionals
* Calling more than one class constructor
* Multiple asserts that aren't related

Simple tests also run faster, and the faster your tests run the less impediment to running them (see Tests Should be Heeded, below). There's a feedback cycle, a certain flow state we're trying to maintain here, and we want to keep that cycle as short as possible.

### Tests Should be Automated

When it comes to tedious checklist-driven stuff like testing code the human will *always* be the weakest link. No matter how disciplined and contentious you may be [7 +- 2](https://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two) will get you. You can use various tools to ensure that you run your tests like git commit hooks, CI/CD servers, and IDE integration (run tests [on file save](https://code.visualstudio.com/docs/python/testing#_example-test-walkthroughs)).

### Tests Should Be Heeded

Never deploy if all the tests don't pass. **NEVER DEPLOY IF ALL THE TESTS DON'T PASS.** As soon as you lose that discipline and get into the game of "we know these tests dont pass but it's ok" you've thrown out most of the value because now fallible distracted conflict-of-interest-ridden human judgement has replaced certain repeatable verifiable automated process. Be aggressive about disabling/removing tests that have lost relevance. Be relentless about updating tests to match code changes.

Heed the design feedback your tests are giving you. If your code is hard to test, it's probably poorly-written. **IF YOUR CODE IS HARD TO TEST, IT'S PROBABLY POORLY-WRITTEN.** Be intentional about reworking code to be amenable to unit testing. Don't take shortcuts, things *always* get bigger over time.

Don't *be* a tool: *use* one.
## *When* Should You Write the Tests?

This is a matter of some debate. There is a movement in the programming community for what is called Test-Driven Development (TDD). In TDD, you write the test *first*. Then you run them to make sure it fails, because you can definitely have a false negative where a test passes even when the code is wrong! This is how you test the test itself. *Then* you write the code, then you make sure the tests pass. I think TDD can be overkill in many cases (it's a lot easier if you already have a formal spec for what a function should do, like the CIDR -> netmask example). But there is one time when you will definitely want to do it: when fixing a bug. Fixing a bug goes like this:

1. Get bug report
2. Verify and reproduce
3. ~~Fix the bug~~ NO! DO NOT FIX THE BUG
4. *Write a test* that reproduces the bug, i.e. fails
5. Fix the bug
6. *Verify the bug is fixed and the tests pass*

As I said above, it's easier when you already have a spec, and in this case you do (or should), in the form of your existing but obviously non-comprehensive test suite. This bug has already made it out of dev and into staging or production *once*, and that's one time too many. You really want to dot all the i's and cross all the t's here. Yet I frequently see people take a perfunctory attitude towards writing bug repro tests, relying on their mental model to make sure they've captured what they think they captured with the bug regression test. May I hunbly suggest that right after you receive incontrovertible proof that your mental model of the world is wrong is maybe not the very best time to put a bunch of stock in it.

## Static Analysis and Linting

Static type annotations can reduce the number of trivial tests you write to verify inputs and outputs. You can check them with the `mypy` tool, like `pytest` is probably ok to install globally. Linting (I like `pylint`) in addition to making your code better-organized and more readable will catch simple errors like typos, bad indentation, and invalid syntax and can and should be integrated with your editor. Use them. The `pylint` tool will give your code a numeric score of up to 10.0 for perfectely grammatical code, I aim for 9+ in every file I write. Much like with failing tests, **NEVER DEPLOY IF THE TYPES DON'T CHECK** unless you are very, *very* certain the tool is wrong and your are right. In other words, unlike tests it's ok to bend this a *little* bit, mostly because Python's type system isn't very powerful and there will be times it will complain about correct code. But again tread very carefully about this (solicit feedback from peers) and be sure to document any instances of this in code comments.

## Wrapping up

Testing is like flossing, or not eating junk food, or insert-task-you-know-you-should-do-but-probably-don't. Part of the reason I'm harping so hard on this is because almost everybody sees the benefits intellectually but then faces decisions in the trenches where the expedient thing isn't at all the best thing. It's a cultural thing: if we don't reinforce each other in maintaining good code habits, well, entropy is the default state of the system. More than most, this is an area where we can uplift each other to be better engineers, provide more value to our organization and our customers, and leave things in a better place than you found them. **NOTE: tell Rod Johnson story**.

Don't be the last guy that we all complain about who left us a mess to untangle. 
