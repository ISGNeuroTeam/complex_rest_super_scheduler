# super_scheduler

Plugin for [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Deploy [complex rest](https://github.com/ISGNeuroTeam/complex_rest/tree/develop)

### Installing

* Make symlink for ./super_scheduler/super_scheduler in plugins directory
* Run complex rest server

## New task creation
 - Open file *super_scheduler/tasks.py*.
 - Create function with args and kwargs inner wrapper *app.task()*: 
   - use args with type *str* and convert only inside the function;
   - if *bind=True* in wrapper, add argument *self* which allows use extra params, for example, task id;
   - always use ***kwargs* if use class *BaseTask*, need for correct work task disabling after many fails;

Examples:
```python
@app.task()
def example_task1(arg1: str, arg2: str):
    pass

@app.task(bind=True)
def example_task2(self, arg1: str, arg2: str):
    pass

@app.task(
    base=BaseTask,
    bind=True,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    result_extended=True,
    retry_kwargs={
        'max_retries': MAX_RETRIES,
        'retry_jitter': RETRY_JITTER,
        'retry_backoff_max': MAX_RETRY_BACKOFF,
    },
)
def best_example_task_3(self, arg1: str, arg2: str, **kwargs):
    pass
```

## Running the tests
Run all tests:
```bash
python ./complex_rest/manage.py test ./plugin_dev/super_scheduler/tests --settings=core.settings.test
```

## Deployment

* Make plugin archive:
```bash
make pack
```
* Unpack archive into complex_rest plugins directory

## Built With

* [Django](https://docs.djangoproject.com/en/3.2/) - The web framework used


## Contributing

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors
Artem Kushch

## License

[OT.PLATFORM. License agreement.](LICENSE.md)

## Acknowledgments
* [otl_interpreter](https://github.com/ISGNeuroTeam/otl_interpreter) - Otl interpreter for platform architecture 2.0.