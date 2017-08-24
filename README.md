# zops.anatomy

Apply and maintain project templates.

# Architecture

The problem we're trying to solve is divided into two parts: defining templates and using template.


The solution for defining templates is called Anatomy Engine and it's composed by the following three concepts:

* Anatomy file
* Anatomy tree
* Anatomy feature

Even though the final objective is to create a tree of files, these files are always generated indirectly by features. A
feature can create or add new content to any file the tree. For example, a feature that configure the PyCharm IDE
(ide-pycharm) may add a mask in the `.gitignore` file. The same is done by the feature that configures Eclipse IDE
(ide-eclipse):

```yaml
# ide-pycharm
add-file-block:
  filename: .gitignore
  contents: |
    /.idea/
```

```yaml
# ide-eclipse
add-file-block:
  filename: .gitignore
  contents: |
    /.project
    /.pydevproject
```

The solution for using the templates is solved using the concept Anatomy playbook. The Anatomy playbook configures which
features will be applied in a directory and tweaks each feature as it see fit for its needs.

```yaml
features:
  - app-django-api
```
