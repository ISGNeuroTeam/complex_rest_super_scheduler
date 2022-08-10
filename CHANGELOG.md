# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Add
 - New args: priority, start_time, expires
 - New flags: disable
 - New fields in config
 - Base celery class
 - Retries functional
 - Auto disabling task after many fails 2 ways:
   - match task, args and kwargs, then disable ones
   - save in kwargs periodic task name and use it for disabling (add in format validating)
 - Add timeouts after task fails and task trash cleaning
 - Restriction on against starting a task before the end of the previous one

### Updated
 - Updated printing and logging
 - Output format '--get' request
 - Periodic task and schedule formats

### Fixed
 - Renamed 'crontab.py', change russian 'С' to english 'C'

### Changed
 - New argparser

## [0.1.0] - 2022-07-15
### Add
 - Main functional

