# Terraform environments checker

This script is useful to check changes in several Terraform environments.

## Getting Started

You need an environment with `python3.7` or avobe.
You need to install the requirements in requirements.txt with pip:
`pip3 install -r requirements.txt`


### How to exclude directories from the check

- Copy the example file "check_envs.ini.example" in the folder where you are launching python script as "check_envs.ini".
- Fullfill the file with paths to exclude.


## Contributing

Feel free to open a PR!


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## To Do

- Parametrize basedir (and allow it as argv)
- Parametrize subdirs (and allow it as argv)
- Parametrize `get_matching_folders` to allow different patterns
- Add tests
- Update flag processing


## Clarification

At this point we have two sets of environments, one following a "legacy" approach with all the code in the application/environment folder, and a new approach with manifests and environments, this is why there are two get_folders, inits and plans in the main function. As soon as we were able to solve this separation we will update the script with only one loop.
