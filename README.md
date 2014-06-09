SublimeSBT
==========
Scala [SBT](http://www.scala-sbt.org/) build tool integration for
[Sublime Text 2](http://sublimetext.com/2) and
[Sublime Text 3](http://sublimetext.com/3).

Features
--------
  - Compatible with Sublime Text 2 and Sublime Text 3.
  - Runs SBT as an interactive REPL inside Sublime Text's output panel.
  - Detects compile errors and test failures in SBT's output and highlights the
    errant lines in the source code.
  - Lists compile errors and test failures in a quick panel for easy navigation
    to the errant lines.
  - Cycles through errors for even faster navigation.
  - Displays the error text in an output panel for easy reading.
  - Detects Play Framework projects and runs SBT using `play` instead of `sbt`.
  - Supports project-specific configuration.

Installing
----------
Download [Package Control](http://wbond.net/sublime_packages/package_control)
and use the *Package Control: Install Package* command from the command palette.
Using Package Control ensures SublimeSBT will stay up to date automatically.

Using
-----
SublimeSBT is mostly used through the Command Palette. To open the pallete,
press `ctrl+shift+p` (Windows, Linux) or `cmd+shift+p` (OS X). The SublimeSBT
commands are all prefixed with `SBT:`. The commands only show up in the command
palette if SublimeSBT detects that your project is an SBT project.

**Start SBT**

  - Start an SBT session for the current project. If the project looks like a
    Play Framework project, the `play` command is used instead of the `sbt`
    command.

**Stop SBT**

  - Stop the currently running SBT session.

**Kill SBT**

  - Force the currently running SBT session to stop.

**Show SBT Output**

  - Show the SBT output panel if it's not already showing. This also focuses
    the output panel and puts the cursor at the end.

**Compile, Test, Run, Package, Start Console**

  - Run the `compile`, `test`, `run`, `package`, or `console` SBT command. If
    SBT is currently running the command is run in interactive mode, otherwise
    it's run in batch mode.

**Start Continuous Compiling, Start Continuous Testing**

  - Run `~ compile` or `~ test`. If SBT is currently running the command is run
    in interactive mode, otherwise it's run in batch mode.

**Test-Only, Test-Quick**

  - Run the `test-only` or `test-quick` command, prompting for an argument. If
    SBT is currently running the command is run in interactive mode, otherwise
    it's run in batch mode.

**Start Continuous Test-Only, Start Continuous Test-Quick**

  - Run `~ test-only` or `~ test-quick`, prompting for an argument. If SBT is
    currently running the command is run in interactive mode, otherwise it's
    run in batch mode.

**Reload**

  - Run the `reload` command if SBT is currently running.

**Show Error List**

  - Show a quick panel with any compile errors or test failures. Selecting an
    error opens the file at the line with the error and shows the error text in
    the error output panel.

**Show Next Error**

  - Jump to the next error in the error list. Opens the file at the line with
    the error and shows the error text in the error output panel.

**Show Error Output**

  - Show the error output panel if it's not already showing.

**Clear Errors**

  - Clear any compile errors or test failures and remove any highlighting
    thereof.

**Show History**

  - Show a quick panel with the history of submitted commands. Selecting a
    command submits it again.

**Show History and Edit**

   - As for Show History but also provides an opportunity to edit the selected
     command before it is re-submitted.

**Clear History**

  - Clear the command history.

Configuring
-----------
The default settings can be viewed by accessing the ***Preferences >
Package Settings > SublimeSBT > Settings – Default*** menu entry. To ensure
settings are not lost when the package is upgraded, make sure all edits are
saved to ***Settings – User***.

**sbt_command**

  - An array representing the command line to use to start sbt. Depending on
    your setup you may need to put the full path to the file here.

**play_command**

  - An array representing the command line to use to start sbt for a Play
    Framework project. Depending on your setup you may need to put the full
    path to the file here.

**test_command**

  - A string representing the sbt command to use to run tests.

**run_command**

  - A string representing the sbt command to use to run the project.

**error\_marking, failure\_marking, warning\_marking**

  - How to mark errors, failures, and warnings in the source code:

    **style**

      - The mark style to use. Valid values are "dot", "outline", or "both".

    **scope**

      - The scope to use to color the outline.

**color_scheme**

  - The color scheme to use for the output panel.

Project-specific settings can be configured by accessing the ***Project > Edit
Project*** menu entry and putting settings in a "SublimeSBT" object inside of
"settings" in your project file, e.g.:

    {
        "folders":
        [
            {
                "path": "/Users/jarhart/scalakoansexercises"
            }
        ],
        "settings":
        {
            "SublimeSBT":
            {
                "sbt_command": ["./sbt"],
                "test_command": "test-only org.functionalkoans.forscala.Koans"
            }
        }
    }

**history_length**

  - The maximum number of unique commands to keep in the command history.
    The default setting is 20.

Contributors
------------
  - [Jason Arhart](https://github.com/jarhart)
  - [Alexey Alekhin](https://github.com/laughedelic)
  - [Colt Frederickson](https://github.com/coltfred)
  - [Bryan Head](https://github.com/qiemem)
  - [Tony Sloane](https://github.com/inkytonik)
  - [Tim Gautier](https://github.com/timgautier)

Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Added some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request

Copyright
---------

Copyright (c) 2012 Jason Arhart. See LICENSE for further details.
