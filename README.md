# Ballista

Ballista is Katello/Red Hat Satellite 6 command-line tool which makes some admin tasks easier (and faster). It originated as an extension of the hammer-cli to do things that are not implemented in hammer. It's designed to be modular as all actions are separated module files. It has a hammer like syntax and is also fully configurable with only an ini configuration file.

## Current features/modules

### Chain publishing of Content Views

With Ballista it's possible in a single step to publish a new version of one or more Content View(s) and automatically attach them to the related Composite Content Views. When the new version is published the Composite Content Views will also be published to a new version.

### Mass promote Content Views to a Lifecycle environment

When the chain publishing is done and you want to make the new versions visible to a Lifecycle environment (for example in a new patch period) you can use Ballista to promote multiple Content Views to a Lifecycle environment with one single command.

### Cleanout Content View versions

Every version of a Content View stays in your system and won't be cleaned automatically. With Ballista you can cleanout (all) your Content Views with one single command and optional keep a set of previous versions.

## Usage

    usage: ballista.py [-h] [--list] [-v] [-c CONF_FILE] [--url URL] [-u USERNAME]
                   [-p] [--organization ORGANIZATION]
                   {chain-publish,promote-env,cleanout-view} ...

    positional arguments:
      {chain-publish,promote-env,cleanout-view}
                            sub-command help
        chain-publish       Publish a content view and all composites that contain
                            it
        promote-env         Mass promote a environment to all given contentviews
        cleanout-view       Cleanup of content view versions

    optional arguments:
      -h, --help            show this help message and exit
      --list                List available actions.
      -v, --verbose
      -c CONF_FILE, --conf_file CONF_FILE
                            path to the file with the Satellite 6 config
      --url URL             Url to connect to (for example
                            https://satellite6.example.com).
      -u USERNAME, --username USERNAME
      -p                    Ask for password on the command line.
      --organization ORGANIZATION
                            Name of the organization

## Examples

### Content View example layout  

| Content View | Contains |
|---|---|
| CV_test1 | Product repositories |
| CV_test2 | Product repositories |
| COMP_test1 | CV_test1 |
| COMP_test2 | CV_test2 |

### Example commands

**Chain publishing:**  
This command will publish a new version in the Content Views CV\_test1 and CV\_test2. Then it attaches and publish them automatically in the Composite Content Views COMP\_test1 and COMP\_test2:

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization chain-publish CV_test1 CV_test2

**Mass promotion:**  
This command promotes the Composite Content Views COMP\_test1 and COMP\_test2 to the "dev" Lifecycle environment:

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization promote-env COMP_test1 COMP_test2 -e dev

**Cleanout old versions:**  
This command will clean the old versions in Composite Content View COMP\_test1 and keeps the the versions which are promoted including the last 3 versions:  

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization cleanout-view COMP_test1 --keep 3
    
And this will clean the old versions in all (Composite) Content Views and keeps only the versions which are promoted:  

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization cleanout-view --all

## Ini configuration file

All above command line options can also be defined in an ini configuration file in the main section. (Composite) Content Views can be defined in separate sections. You can give these sections as parameters instead of Content View names.

**Example Ini file:**

    [main]
    url = https://satellite.example.com
    organization = Example_organization
    username = <username>
    password = <password>

    # layout for example above commands
    [publish]
    views = CV_test1, CV_test2

    [promote]
    views = COMP_test1, COMP_test2

    # business example with separate os and middleware patching
    [os]
    views = CV_RHEL6, CV_RHEL7, CV_PuppetModules

    [middleware]
    views = CV_JBoss, CV_WebSphere

    [os-patch]
    views = COMP_RHEL6, COMP_RHEL7, COMP_RHEL6_WebSphere, COMP_RHEL7_JBoss
    
    [middleware-patch]
    views = COMP_RHEL6_WebSphere, COMP_RHEL7_JBoss

# Authors
Ballista is written by Yoram Hekma <hekma.yoram@gmail.com> and Joey Loman <joey@binbash.org>.