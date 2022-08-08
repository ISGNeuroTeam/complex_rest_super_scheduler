# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Add
 - New args: priority, start_time
 - New flags: disable
 - New fields in config
 - Base celery task
 - Retries functional
 - Auto disabling task after many fails
 - Timeouts after fails and tasks trash cleaning

### Updated
 - Updated printing and logging
 - Output format '--get' request
 - Periodic task and schedule formats

### Fixed
 - Renamed 'crontab.py', change russian 'С' to english 'C'

## [0.1.0] - 2022-07-15
### Add
 - Main functional

