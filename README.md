SublimeSBT
==========
Run the [SBT](http://www.scala-sbt.org/) build tool inside
[Sublime Text 2](http://sublimetext.com/2).

SublimeSBT runs SBT as an interactive REPL inside the Sublime Text 2's output
panel.

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
  Play Framework project, the `play` command is used instead of `sbt`.

**Stop SBT**

 - Stop the currently running SBT session.

**Kill SBT**

 - Force the currently running SBT session to stop.

**Show SBT Output**

 - Show the SBT output panel if it's not already showing.

**Compile, Test, Run, Start Console**

 - Run the `compile`, `test`, `run`, or `console` SBT command. If SBT is
  currently running the command is run in interactive mode, otherwise it's run
  in batch mode.

**Start Continuous Compiling, Start Continuous Testing**

 - Run `~ compile` or `~ test`. If SBT is currently running the command is run
 in interactive mode, otherwise it's run in batch mode.

Configuring
-----------
The default settings can be viewed by accessing the ***Preferences >
Package Settings > SublimeSBT > Settings – Default*** menu entry. To ensure
settings are not lost when the package is upgraded, make sure all edits are
saved to ***Settings – User***.

**sbt_command**

 - An array representing the command line to use to start sbt.

**play_command**

 - An array representing the command line to use to start sbt for a Play
  Framework project.

**color_scheme**

 - The color scheme to use for the output panel. Only the default foreground
  and background colors are used.
