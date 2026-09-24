#!/usr/bin/env python
import os
import sys

# You can find documentation for SCons and SConstruct files at:
# https://scons.org/documentation.html

# This lets SCons know that we're using godot-cpp, from the godot-cpp folder.
env = SConscript("godot-cpp/SConstruct")

# Configures the 'src' directory as a source for header files.
env.Append(CPPPATH=["src/"])

# Collects all .cpp files in the 'src' folder as compile targets.
sources = Glob("src/*.cpp")

if env["target"] in ["editor", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData("src/gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml"))
        sources.append(doc_data)
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.3 baseline.")

# The filename for the dynamic library for this GDExtension.
# $SHLIBPREFIX is a platform specific prefix for the dynamic library ('lib' on Unix, '' on Windows).
# $SHLIBSUFFIX is the platform specific suffix for the dynamic library (for example '.dll' on Windows).
# env["suffix"] includes the build's feature tags (e.g. '.windows.template_debug.x86_64')
# (see https://docs.godotengine.org/en/stable/tutorials/export/feature_tags.html).
# The final path should match a path in the '.gdextension' file.
lib_filename = "{}StarterTemplate{}{}".format(env.subst('$SHLIBPREFIX'), env["suffix"], env.subst('$SHLIBSUFFIX'))

# Creates a SCons target for the path with our sources.
library = env.SharedLibrary(
    "project/addons/StarterTemplate/bin/{}".format(lib_filename),
    source=sources,
)

# Selects the shared library as the default target.
Default(library)

# --- Unit tests (tests/) ---
# Builds and runs a native, engine-independent test program (no godot-cpp
# linking, no running Godot process required) for any pure logic added to
# src/. Uses its own native Environment rather than the (possibly
# cross-compiling) `env` above, since the test binary needs to run on this
# machine.
test_env = Environment()
test_env.Append(CPPPATH=["src/"])
if test_env["CXX"] == "cl":
    test_env.Append(CXXFLAGS=["/std:c++17"])
else:
    test_env.Append(CXXFLAGS=["-std=c++17"])

test_program = test_env.Program("tests/bin/test_StarterTemplate", Glob("tests/*.cpp"))
run_tests = test_env.Alias("tests", test_program, test_program[0].abspath)
AlwaysBuild(run_tests)

# --- Docs update (doc_classes/) ---
# Regenerates doc_classes/*.xml from the classes' _bind_methods() by loading
# the built extension into Godot's --doctool. Requires a template_debug build
# (with doc data compiled in, see the GodotCPPDocData block above) and a
# flatpak install of the Godot editor (org.godotengine.Godot). Run with
# `scons docs`. Runs from project/ since --doctool needs a Godot project
# (project.godot) to load the extension into.
update_docs = Command(
    "update_docs",
    None,
    "flatpak run org.godotengine.Godot --doctool ../ --gdextension-docs",
    chdir="project",
)
docs_alias = Alias("docs", update_docs)
AlwaysBuild(update_docs)
