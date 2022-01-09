## The Four Commands You Need To Know

1. `pip install -e .[dev]`

    This will install your package in editable mode with all the required development
    dependencies (i.e. `tox`).

2. `make build`

    This will run `tox` which will run all your tests in both Python 3.7
    and Python 3.8 as well as linting your code.

3. `make clean`

    This will clean up various Python and build generated files so that you can ensure
    that you are working in a clean environment.

4. `make docs`

    This will generate and launch a web browser to view the most up-to-date
    documentation for your Python package.

#### Additional Optional Setup Steps:

-   Turn your project into a GitHub repository:
    -   Make an account on [github.com](https://github.com)
    -   Go to [make a new repository](https://github.com/new)
    -   _Recommendations:_
        -   _It is strongly recommended to make the repository name the same as the Python
            package name_
        -   _A lot of the following optional steps are *free* if the repository is Public,
            plus open source is cool_
    -   After a GitHub repo has been created, run the commands listed under:
        "...or push an existing repository from the command line"
-   Register your project with Codecov:
    -   Make an account on [codecov.io](https://codecov.io)(Recommended to sign in with GitHub)
        everything else will be handled for you.
-   Ensure that you have set GitHub pages to build the `gh-pages` branch by selecting the
    `gh-pages` branch in the dropdown in the "GitHub Pages" section of the repository settings.
    ([Repo Settings](https://github.com/lmkawakami/didatictests/settings))
-   Register your project with PyPI:
    -   Make an account on [pypi.org](https://pypi.org)
    -   Go to your GitHub repository's settings and under the
        [Secrets tab](https://github.com/lmkawakami/didatictests/settings/secrets/actions),
        add a secret called `PYPI_TOKEN` with your password for your PyPI account.
        Don't worry, no one will see this password because it will be encrypted.
    -   Next time you push to the branch `main` after using `bump2version`, GitHub
        actions will build and deploy your Python package to PyPI.

#### Suggested Git Branch Strategy

1. `main` is for the most up-to-date development, very rarely should you directly
   commit to this branch. GitHub Actions will run on every push and on a CRON to this
   branch but still recommended to commit to your development branches and make pull
   requests to main. If you push a tagged commit with bumpversion, this will also release to PyPI.
2. Your day-to-day work should exist on branches separate from `main`. Even if it is
   just yourself working on the repository, make a PR from your working branch to `main`
   so that you can ensure your commits don't break the development head. GitHub Actions
   will run on every push to any branch or any pull request from any branch to any other
   branch.
3. It is recommended to use "Squash and Merge" commits when committing PR's. It makes
   each set of changes to `main` atomic and as a side effect naturally encourages small
   well defined PR's.

---

## Local dev.: step by step

1. config. VSCode and WSL things [help](https://ruslanmv.com/blog/Python3-in-Windows-with-Ubuntu)
2. open WSL
3. run `sudo apt update`
4. run `sudo apt -y upgrade`
5. check python3 version `python3 -V`
6. install pip `sudo apt install -y python3-pip`
7. run `sudo apt install -y build-essential libssl-dev libffi-dev python3-dev`
8. install venv `sudo apt install -y python3-venv`
9. navigate to the folder where the environment will be created (`cd ..`, `cd SOME_DIR`)
   ex.:
   1. `mkdir environments`
   2. `cd environments`
10. create the "didatictests" environment `python3 -m venv didatictests`
11. activate the virtual environment `source didatictest/bin/activate`
12. enter `cd didatictest`
13. clone the repo `git clone https://github.com/lmkawakami/didatictests.git`
14. enter `cd didatictest`
15. open VSCode `code .`
16. install your package in editable mode with all the required development dependencies (i.e. tox) `pip install -e .[dev]`
17. install the python3 versions that you don't have [help](https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/)
    1.  check if you have python3.7, 3.8 and 3.9 `python3.7 --version`, `python3.8 --version`, `python3.9 --version`
    2.  add the deadsnakes PPA to your sources list `add-apt-repository ppa:deadsnakes/ppa`
    3.  install any version that you don't have `apt install python3.7`,`apt install python3.8`,`apt install python3.9`
18. build the project `make build`
19. to publish a new version, use bumpversion: `bumpversion patch --verbose` [help1](https://bump2version.readthedocs.io/en/latest/examples/semantic-versioning/) [help2](https://pypi.org/project/bumpversion/)