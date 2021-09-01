import time
import random

import cfnlint.core

import boto3
cfn = boto3.client('cloudformation')


def run_cfn_lint(filename):
    args, filenames, formatter = cfnlint.core.get_args_filenames([filename])
    template, rules, template_matches = cfnlint.core.get_template_rules(
        filename, args)
    if template_matches:
        print(formatter.print_matches(template_matches))
        return False
    matches = cfnlint.core.run_cli(filename, template, rules, args.regions,
                                   args.override_spec, build_graph=False,
                                   registry_schemas=None)
    if matches:
        print(formatter.print_matches(matches))
        return False
    return True


def generate_name(filename):
    randhex = "".join(random.choice("0123456789abcdef") for i in range(5))
    return f'sonde-{randhex}'


def launch_template(filename, stack_name):
    with open(filename) as fp:
        template_body = fp.read()
        
    response = cfn.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND']
    )
    stack_id = response['StackId']

    # wait for stack to stabilize
    printed_events = set()
    while True:
        response = cfn.describe_stack_events(StackName=stack_id)
        events = response['StackEvents']
        for event in events:
            if event['EventId'] not in printed_events:
                print(event['LogicalResourceId'],
                      event['ResourceType'],
                      event['ResourceStatus'],
                      event.get('ResourceStatusReason', ''))
                printed_events.add(event['EventId'])
            if (event['LogicalResourceId'] == event['StackName']
                and event['ResourceType'] == 'AWS::CloudFormation::Stack'
                and 'IN_PROGRESS' not in event['ResourceStatus']):
                return
        time.sleep(2)

def verify_template(stack_name):
    response = cfn.describe_stack_events(StackName=stack_name)
    events = response['StackEvents']
    for event in reversed(events):
        if not (event['LogicalResourceId'] == event['StackName']
            and event['ResourceType'] == 'AWS::CloudFormation::Stack'):
            continue
        print('Final state:', event['ResourceStatus'])
        return event['ResourceStatus'] == 'CREATE_COMPLETE'

def cleanup_template(stack_name):
    print('Deleting...', stack_name)
    cfn.delete_stack(StackName=stack_name)


class TestRunner:
    def __init__(self):
        self.paths = []

    def run(self):
        results = []
        for path in self.paths:
            if not run_cfn_lint(path):
                results.append(False)
                continue

            try:
                name = generate_name(path)
                launch_template(path, name)
                verify_template(name)
            finally:
                cleanup_template(name)
            
        return all(results)
