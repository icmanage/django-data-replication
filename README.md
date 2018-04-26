# Django Data Replication

This will allow you to replicate data to another place - Like mongo for analytics.

Learn more https://github.com/icmanage/django-data-replication.

### Build Process:
1.  Update the `__version_info__` inside of the application. Commit and push.
2.  Tag the release with the version. `git tag <version> -m "Release"; git push --tags`
3.  Build the release `rm -rf dist build *egg-info; python setup.py sdist bdist_wheel`
4.  Upload the data `twine upload dist/*`
