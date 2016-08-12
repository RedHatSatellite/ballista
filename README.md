# Ballista

Ballista is a Katello/Red Hat Satellite 6 command-line tool which makes some admin tasks easier (and faster). Its original goal is to act as a supplement to the hammer-cli, providing functionality that hammer does not. Because of its modular design all subcommand logic is contained in seperate modules, so it is easy to extend its functionality. It has a hammer-like syntax and can optionally use a standard configuration file for default parameters such as Katello/Satellite6 url and organization.

## Current features/modules

### Compute resource profile import/export

The newly added compute-resource-profiles option allows you to import or export all your compute profiles. This saves you a lot of clicking in the webinterface and (in case of vmware) wait times everytime the virtualization objects are downloaded during a compute profile selection. For example: you can configure one complete compute profile and export it. Then you can use the exported json file as a template to create the rest of the profiles by creating multiple json files in the same directory. When al the profiles are saved you can import them with a single ballista command (which only takes seconds) and keep them as a backup for future imports.

### REPL (read-evaluate-print-loop)

You can use the (not quite finished yet) repl interface to interactively list and promote your content views:

```
[nix-shell:~/Dev/ballista]$ ./ballista.py -c example_config.ini repl
(Cmd) help

Documented commands (type help <topic>):
========================================
exit  help  list_cviews  promote

Undocumented commands:
======================
EOF

(Cmd) help list_cviews
Print content views.Pass -j to list them in all their json glory, -v to list the versions of the views as well
(Cmd) list_cviews -v
Default Organization View
    Version: 1.0 (2016-06-13 12:10:37 UTC)
Comp2
    Version: 1.0 (2016-06-13 13:06:33 UTC)
Comp1
    Version: 1.0 (2016-06-13 13:06:16 UTC)
    Version: 2.0 (2016-06-13 14:03:08 UTC)
----- snip -----
(Cmd) help promote
Promote a content view to a givent environment. Optionally you can specify a version.
Promote newest version:
   promote <content view name> <environment>
promote specific version:
   promote <content view name>/<version> <environment>
(Cmd) promote Comp2 Devel
(Cmd)
```


### Chain publishing of Content Views

With Ballista it's possible to publish a new version of one or more Content Views and automatically attach them to the related Composite Content Views with a single command. When the new version is published the Composite Content Views that contain the newly published Content View will also be published to a new version. Note that this new version is not yet promoted, so you still have control over your normal patch and lifecycle management.

### Mass promote Content Views to a Lifecycle environment

Using a single command you can promote the newest version of multiple Content Views to a Lifecycle Environment. This is especially useful when combined with the chain-publishing feature, as you can first update your baseviews and then mass-promote the resulting versions of the Composite Content Views when you actually want to have the content available to your hosts in that environment (ie. when you want to patch).

### Cleanout Content View versions

In order to be able to roll back to a previous version of a Content View, previous versions are never removed by Katello/Satellite6. Removing old and obsolete versions can be a time consuming manual (and thus error-prone) operation. With Ballista you can remove all unused versions of a Content View, optionally supplying a number of recent versions to keep. If you have a lot of content views, you can also clean all of them in one go.

## Usage

    usage: ballista.py [-h] [--list] [-v] [-c CONF_FILE] [--url URL] [-u USERNAME]
                       [-p] [--organization ORGANIZATION]
                       {cleanout-view,repl,compute-resource-profiles,chain-publish,promote-cv}
                       ...

    positional arguments:
      {cleanout-view,repl,compute-resource-profiles,chain-publish,promote-cv}
                            sub-command help
        cleanout-view       Cleanup of content view versions
        repl                Start repl-shell
        compute-resource-profiles
                            Export or import compute resource profiles
        chain-publish       Publish a content view and all composites that contain
                            it
        promote-cv          Mass promote a environment to all given contentviews
    
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
    --organization Example_organization promote-cv dev COMP_test1 COMP_test2

**Cleanout old versions:**  
This command will clean the old versions in Composite Content View COMP\_test1 and keeps the the versions which are promoted including the last 3 versions:  

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization cleanout-view COMP_test1 --keep 3

And this will clean the old versions in all (Composite) Content Views and keeps only the versions which are promoted:  

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization cleanout-view --all

**Exporting compute profiles:**  
This command exports all compute profiles configured for the "VirtualCenterHost" compute resource host to the /tmp/ballista-compute-profiles directory:

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization compute-resource-profiles \
    -cr VirtualCenterHost -e -p /tmp/ballista-compute-profiles

And this command imports all compute profiles located in the directory /tmp/ballista-compute-profiles and configure them for the "VirtualCenterHost" compute resource host:

    ./ballista.py --url https://satellite.example.com -u admin -p \
    --organization Example_organization compute-resource-profiles \
    -cr VirtualCenterHost -i -p /tmp/ballista-compute-profiles

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

# Contributing/keeping up-to-date
Ballista is maintained primarily at [Github](https://github.com/RedHatSatellite/ballista). Merge requests or issues should be created there.

# Authors
Ballista is written by Yoram Hekma <hekma.yoram@gmail.com> and Joey Loman <joey@binbash.org>.
