# StarterTemplate-GDExtension

A starter template to make a native GDExtension. Based on (https://docs.godotengine.org/en/stable/tutorials/scripting/cpp/gdextension_cpp_example.html)

* Has GDExtension documentation support (rebuild with `scons docs`)
* Updates wiki docs from a github action, from the godot docs
* Build action builds and runs tests
* Release action will .zip the addon and append it to any release with a `vX.X.X` tag format
