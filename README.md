# Terraform environments checker

This script is useful to check changes in one (or several) Terraform environments.

## Getting Started

You need an environment with `python3.7` or avobe.
You need to install the requirements in requirements.txt with pip:
`pip install -r requirements.txt`


### How to use (customizations)
At this point is not possible to configure through parameters (it will arrive ASAP), so:
- Configure `basedir`, if your terraform environments are under `/home/USER/tf_environments/` change this value.
- Configure `subdirs`: This "variable" allows you to define which subdirectories will be checked for terraform files, so if you want to check only application php/backend, you need to set as `php/backend`, or even, if you want to check only prod for this application `php/backend/prod`.
- Configure `EXCLUDE_PATHS_LIST` in order to exclude these directories.


## Contributing

Feel free to open a PR!


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## To Do

- Parametrize basedir (and allow it as argv)
- Parametrize subdirs (and allow it as argv)
- Parametrize `get_matching_folders` to allow different patterns
- Add tests
- Paralelize some of the steps (terraform init could be launched in parallel)
- Update flag processing


## Clarification

At this point we have two sets of environments, one following a "legacy" approach with all the code in the application/environment folder, and a new approach with manifests and environments, this is why there are two get_folders, inits and plans in the main function. As soon as we were able to solve this separation we will update the script with only one loop.
