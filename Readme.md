<h1>NR-NSA Systems Topology</h1>

- [Confluence](#confluence)
- [Enivronment Setup](#enivronment-setup)
- [Concept Overview](#concept-overview)
- [Structure Overview](#structure-overview)
- [File Overview](#file-overview)
- [Documentation](#documentation)
- [Testing](#testing)
- [Running the Script](#running-the-script)

## Confluence
Here is a [confluence page](https://confluence-nam.lmera.ericsson.se/display/ENMRANEO/NR-NSA) that contains the below information and also some further details.

## Enivronment Setup

To get your environment setup, here are some helpful steps.

<span style="color:#f29429;">
    <h3>IDE</h3>
</span>

You can use more or less any IDE or Text Editor, they should have some plugin to support python.
The likes of Pycharm, which is a python specific IDE has a lot of builtin support out of the box.

Vs Code offers a rich extension library which can enable quick python development also.

<span style="color:#f29429;">
    <h3>Installing Python</h3>
</span>
ENM specifically uses python 2.6.6

However, you can manage to use python 2.7.X for development as the differences between the versions are not apparent for the work being carried out here.

Once python has been installed, be sure to include it on you PATH if you happen to be using windows.

<span style="color:#f29429;">
    <h3>Virtualenv</h3>
</span>
Python offers virtual environments, which when used, allow you to keep python libraries installed to a particular virtual environment.

This can be particularly helpful if you happen to be working on many python based projects.

To use this feature you simply install Virtualenv
```Linux
pip install virtualenv
```
And once that install has completed you can create a virtual environment

```Linux
Virtualenv my_environment
```

Once this has been created, you will then need to activate the environment like so

```Linux
source my_environment/bin/activate
```

Or if you happen to be using windows

``` Linux
source my_environment/Scripts/activate
```

Your virtual environment is now up and running and you can install the necessary packages.

<span style="color:#f29429;">
    <h3>Installing Packages</h3>
</span>
The following command should install the packages necessary for NR-NSA

```Linux
pip install virtualenv, testfixtures, pylint, mock, coverage, urllib3, requests, nose
```

In the event that you see a module not found error, the `pip install` said module should revolve that issue.

## Concept Overview

NR-NSA systems topology is a modelled Topology that depicts the existing relationships between EnodeB and GnodeB Nodes.

This is necessary at the minute as the new 5G Nodes are 'Non-Standalone' meaning that you cannot have a 5G Node without the support of the exisiting 4G Nodes.
***

## Structure Overview

NR-NSA is a series of python scripts, these scripts are deployed to the scripting vm in ENM. Within these scripts, there is a `setup.py` file.

When `setup.py` is manually executed by a user with the _correct rights_, it will create a new cronjob in the scripting vm. This cronjob, by default is set to run every midnight, in doing so, it will executed the `main.py` file, which as the name suggests, is the main scripting file that will control the execution flow for NR-NSA.

This `main.py` file may also be executed manually by a user with the same _correct rights_.
***
## File Overview

The following files exist in NR-NSA at this time.

* `main.py`
* `setup.py`
* `nrnsa_utils.py`
* `sso_manager.py`
* `network_utils.py`
* `nrnsa_export_utils.py`
* `constants.py`
* `nrnsa_cli.py`
* `nrnsa_exception.py`
* `nrnsa_exception_handler.py`
* `log.py`
* `parser.py`
* `data.py`
* `crypt.py`
* `cookie.text`

The `nrnsa_cli.py` file as the name suggests is the primary file that interacts with the ENM cli application. This file really has only one goal from the point of view of `main.py`. That is to return the relationships that exist at the time of execution.

The `nrnsa_utils.py` file is a utiliy file that handles the interactions with Topology Collection Service as well as Topology Search Service.

The `sso_manager.py` file handles the interactions with the OpenIDM application. This involves ensuring that a correct cookie has been recieved and stored.

The `network_utils.py` file handles interactions with the currently deployed environment. It aims to return the ENM hostname from the environment it is on, be it cloud or physical.

The `log.py` file handles the methods for logging. This includes the usual set of INFO, DEBUG, WARN, ERROR

The `constants.py` file can be used to store constant strings for cleaner readability.

The `data.py` and `parser.py` files are used to handle the parsing of the Termainal Output when interacting with the ENM Cli

The `crypt.py` file is used to handle the interactions needed when storing and hashing the user's password. It writes the hashed password and the keyset to a secure directory and avoides the need for storing an ENM user's password in plain text.

The `nrnsa_exception_handler.py` file allows for the script to print an exception message to the screen without having to print the stacktrace.

The `nrnsa_exports.py` file handles the exporting of the NR-NSA collection.


## Documentation

The following documentation currently exists for NR-NSA.

- `PRI` To describe any new functionality / use cases delivered for NR-NSA in a given sprint.
- `OLH` To describe to the ENM user, what the NR-NSA Topology is.
- `FS` To describe the Functional Summary and Performance Characteristics for NR-NSA.
- `SAG-Configuration` To describe the necessary processes that are needed to configure the setup of NR-NSA

***

## Testing

### Unit Testing

The test cases in place for NR-NSA are largely unit tests. Tests can of course be integration based also, there is little to distinguish between the two in python based applications compared to the more standardized approach you might be familiar with in Javascript / Java applications.

Testing is based on the unittest library which is build into python.

There are many modules within python itself that will allow for mocking a method / object also.

NR-NSA is largely based on a `best-effort` approach, in turn this can make testing slightly more difficult to complete as you cannot also assert what you may want.

For some of the existing Negative based test cases, you may see an assertion that a log message has been captured as opposed to checking that a specific value is returned or expection is raised and that is because of the flow of the script.

One way to run all of the tests is to simply kick of a maven clean install.
One way to run a specific test file is to simply use

``` Linux
nosetests test_log.py
```

### Integration Testing

To execute the integration tests for NR-NSA you should utilize docker.

From the root of the directory execute the following commands


```docker
docker-compose up --build
```

***

## Running the Script

Once you have an RPM & you have installed the RPM on the scripting vm, either svc-2-scripting or scp-1-scripting depending on your environment. You should create an nr-nsa user. This user is necessary to create the NR-NSA Topology as _system created_. The user should have the following roles

- Network_Explorer_Administrator
- Scripting_Operator
- Cmedit_Administrator
- `custom role`

To create the `custom role` user , use the Role Management application. Add the two `system_created_object` resources to this role. Add this role to the NR-NSA user.

Navigate to the scripting VM.

**NOTE** You should ssh in as the nrnsa user. You can then navigate to /opt/ericsson/nr-nsa-systems-topology and run

``` Linux
python main.py
```