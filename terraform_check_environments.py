import argparse
import concurrent.futures
import os
from pathlib import Path, PurePath
import subprocess
from termcolor import colored
import configparser


class tf_environment:

    def __init__(self, path, has_manifest=True):
        self.result = -1
        self.path = path
        self.has_manifest = has_manifest

    def init_command(self):
        extra_argument = ''
        if self.has_manifest:
            extra_argument = '-backend-config=backend.tfvars ../manifests'
        tf_init = 'terraform init ' + extra_argument
        return tf_init

    def plan_command(self):
        extra_arguments = ''
        if self.has_manifest:
            vars_file = PurePath(self.path).name + '.tfvars'
            extra_arguments = '-var-file=' + vars_file + ' ../manifests'
        tf_apply_basic_command = 'terraform plan -input=false -detailed-exitcode '
        tf_plan = tf_apply_basic_command + extra_arguments
        return tf_plan


def print_result_block(envs_list, name, status):
    count = 0
    print("## ", name, " ##")
    for env in envs_list:
        if env.result == status:
            print("  ", env.path)
            count += 1
    return count


def display_results(envs):
    not_executed = print_result_block(envs, "NOT EXECUTED", -1)
    ok = print_result_block(envs, "OK", 0)
    pending_changes = print_result_block(envs, "PENDING CHANGES", 2)
    init_errors = print_result_block(envs, "INIT ERRORS", 5)
    plan_errors = print_result_block(envs, "PLAN ERRORS", 1)
    print("General status:")
    print("TOTAL: ", len(envs))
    print("ENVIRONMENT OK: ", ok)
    print("ENVIRONMENT PENDING CHANGES: ", pending_changes)
    print("ENVIRONMENT ERRORS: ", init_errors + plan_errors)


def terraform_init(env):
    print(colored(f'{env.path}: START terraform init', 'cyan'))
    FNULL = open(os.devnull, 'w')
    subprocess.run(
        'rm .terraform -rf', shell=True, cwd=env.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process = subprocess.run(
        env.init_command(), shell=True, cwd=env.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if process.returncode == 0:
        output_text = colored(f'{env.path}: END terraform init OK', 'green')
    else:
        output_text = colored(
            f'{env.path}: END terraform init FAILED', 'red')
        self.result = 5
    print(output_text)
    return process.returncode


def terraform_plan(env):
    print(colored(f'{env.path}: START terraform plan', 'blue'))
    if env.result == -1:
        process = subprocess.run(
            env.plan_command(), shell=True, cwd=env.path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if process.returncode == 0:
            output_text = colored(
                f'{env.path}: END terraform plan OK', 'green')
        else:
            output_text = colored(
                f'{env.path}: END terraform plan FAILED. Exit code: {process.returncode}', 'red')
        env.result = process.returncode
        print(output_text)


def is_excluded(selected_path, excluded_path):
    return selected_path.as_posix().find(str(excluded_path)) != -1


def is_undesired_path(selected_path, excluded_paths):
    for ep in excluded_paths:
        if is_excluded(selected_path, ep):
            return True
    return False


def get_environments(pattern, excluded_paths=[], with_manifests=True):
    envs_list = []
    paths_list = []
    for filename in Path('.').glob('./' + '**/' + pattern):
        if not is_undesired_path(filename, ['.terraform'] + excluded_paths):
            envs_list.append(
                tf_environment(
                    path=filename.parent,
                    has_manifest=with_manifests
                ))
            paths_list.append(filename.parent)
    return envs_list, paths_list


def get_excluded_paths():
    excluded_paths_list = []

    if os.path.exists('check_environments.ini'):
        config = configparser.ConfigParser(allow_no_value=True)
        # overwrite optionxform method for overriding default behaviour (I didn't want lowercased keys)
        config.optionxform = lambda optionstr: optionstr
        config.read('check_environments.ini')
        excluded_paths_list = list(config['ExcludedPaths'].keys())
    return excluded_paths_list


def main():

    legacy_envs, legacy_paths_list = get_environments(
        pattern='terraform.tf',
        excluded_paths=['manifests'],
        with_manifests=False)
    manifest_envs, _ = get_environments(
        pattern='backend.tfvars',
        excluded_paths=get_excluded_paths() + legacy_paths_list)

    envs = sorted(
        legacy_envs + manifest_envs, key=lambda env: env.path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(terraform_init, envs)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(terraform_plan, envs)

    display_results(envs)


if __name__ == '__main__':
    main()
