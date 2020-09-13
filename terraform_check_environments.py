import argparse
import concurrent.futures
from functools import partial
import os
from pathlib import Path, PurePath
import subprocess
from termcolor import colored
import configparser
from shutil import rmtree


def print_result_block(envs_list, name):
    if not envs_list:
        return 0
    print("## ", name, " ##")
    for environment in envs_list:
        print("  ", environment)


def display_results(results):
    print_result_block(results[0], "NO PENDING CHANGES")
    print_result_block(results[1], "ENVIRONMENTS WITH ERRORS")
    print_result_block(results[2], "PENDING CHANGES")
    print("General status:")
    print("TOTAL: ", len(results[0])+len(results[1])+len(results[2]))
    print("ENVIRONMENT OK: ", len(results[0]))
    print("ENVIRONMENT PENDING CHANGES: ", len(results[2]))
    print("ENVIRONMENT ERRORS: ", len(results[1]))


def get_tf_init_command(with_manifest):
    extra_argument = ''
    if with_manifest:
        extra_argument = '-backend-config=backend.tfvars ../manifests'
    tf_init = 'terraform init ' + extra_argument
    return tf_init


def execute_tf_init_command(tf_init, path):
    FNULL = open(os.devnull, 'w')
    process = subprocess.run(
        tf_init, shell=True, cwd=path, stdout=FNULL)
    if process.returncode == 0:
        output_text = colored(f'{path}: INIT OK', 'green')
    else:
        output_text = colored(
            f'{path}: INIT FAILED with exit code: {process.returncode}', 'red')
    print(output_text)
    return process.returncode


def terraform_init(paths_list, *, with_manifest=False):
    tf_init = get_tf_init_command(with_manifest)
    parallel_init_fn = partial(execute_tf_init_command, tf_init)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(parallel_init_fn, paths_list)


def get_tf_plan_command(path='', with_manifest=False):
    tf_apply_basic_command = 'terraform plan -detailed-exitcode -no-color '
    extra_arguments = ''
    if with_manifest:
        vars_file = PurePath(path).name + '.tfvars'
        extra_arguments = '-var-file=' + vars_file + ' ../manifests'
    tf_plan = tf_apply_basic_command + extra_arguments
    return tf_plan


def execute_tf_plan_command(path, tf_plan):
    print(path, ": ", tf_plan)
    process = subprocess.run(
        tf_plan, shell=True, cwd=path)
    return process.returncode


def terraform_plan(paths_list, with_manifest=False):
    result = {0: [], 1: [], 2: []}
    for path in paths_list:
        tf_apply_command = get_tf_plan_command(path, with_manifest)
        exitcode = execute_tf_plan_command(path, tf_apply_command)
        result[exitcode].append(path)
    return result


def is_excluded(selected_path, excluded_path):
    return selected_path.as_posix().find(str(excluded_path)) != -1


def is_undesired_path(selected_path, excluded_paths):
    for ep in excluded_paths:
        if is_excluded(selected_path, ep):
            return True
    return False


def get_matching_folders(pattern, excluded_paths=[], basedir='./', subdirs='**/'):
    folders_list = []
    for filename in Path('.').glob(basedir + subdirs + pattern):
        if not is_undesired_path(filename, ['.terraform'] + excluded_paths):
            folders_list.append(filename.parent)
    return folders_list


def terraform_clean(paths_list, with_manifest=False):
    for path in paths_list:
        rmtree(str(path) + '/.terraform', ignore_errors=True)


def get_config_excluded_paths_list():
    config = configparser.ConfigParser()
    config.read('config.ini')
    paths_list = [path.strip() for path in config.get(
        "DEFAULT", "EXCLUDE_PATHS_LIST").split(',')]
    return paths_list


def main():
    config_excluded_paths_list = get_config_excluded_paths_list()
    legacy_envs = get_matching_folders(
        'terraform.tf', excluded_paths=['manifests'] + config_excluded_paths_list)
    terraform_clean(legacy_envs)
    terraform_init(legacy_envs)
    result_legacy = terraform_plan(legacy_envs)

    manifest_envs = get_matching_folders(
        'backend.tfvars', excluded_paths=legacy_envs + config_excluded_paths_list)
    terraform_clean(manifest_envs)
    terraform_init(manifest_envs, with_manifest=True)
    result_manifests = terraform_plan(manifest_envs, with_manifest=True)

    display_results({**result_legacy, **result_manifests})


if __name__ == '__main__':
    main()
