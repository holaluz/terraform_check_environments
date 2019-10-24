from pathlib import Path, PurePath
import subprocess


EXCLUDE_PATHS_LIST = [
    'demo',
    'demo2'
]

EXIT_STATUS = {0: [], 1: [], 2: []}


def add_to_results(result, path):
    EXIT_STATUS[result].append(path)


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


def execute_tf_init_command(path, tf_init):
    print(path, ": ", tf_init)
    subprocess.run(
        'rm .terraform -rf', shell=True, cwd=path)
    subprocess.run(
        tf_init, shell=True, cwd=path)


def terraform_init(paths_list, with_manifest=False):
    tf_init = get_tf_init_command(with_manifest)
    for path in paths_list:
        execute_tf_init_command(path, tf_init)


def get_tf_plan_command(path=''):
    tf_apply_basic_command = 'terraform plan -detailed-exitcode -no-color '
    extra_arguments = ''
    if path:
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
    for path in paths_list:
        tf_apply_command = get_tf_plan_command()
        result = execute_tf_plan_command(path, tf_apply_command)
        add_to_results(result, path)


def is_excluded(selected_path, excluded_path):
    return selected_path.as_posix().find(excluded_path) != -1


def is_undesired_path(selected_path, excluded_paths):
    for ep in excluded_paths + EXCLUDE_PATHS_LIST:
        if is_excluded(selected_path, ep):
            return True
    return False


def get_matching_folders(pattern, excluded_paths=[], basedir='./', subdirs='**/'):
    folders_list = []
    for filename in Path('.').glob(basedir + subdirs + pattern):
        if not is_undesired_path(filename, ['.terraform'] + excluded_paths):
            folders_list.append(filename.parent)
    return folders_list


def main():
    legacy_envs = get_matching_folders(
        'terraform.tf', ['manifests'])
    terraform_init(legacy_envs)
    terraform_plan(legacy_envs)

    manifest_envs = get_matching_folders('backend.tfvars')
    terraform_init(manifest_envs, True)
    terraform_plan(manifest_envs, True)

    display_results(EXIT_STATUS)


if __name__ == '__main__':
    main()
