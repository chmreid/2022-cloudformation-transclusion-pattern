import logging
import time
import json
import boto3
import ipaddress

waf_client = boto3.client('wafv2') # Keep this here for mocking
ssm_client = boto3.client('ssm')

def validate_ipv4set(ipv4set):
    for ip in ipv4set:
        addr = ipaddress.ip_address(ip)
        if type(addr) != ipaddress.IPv4Address:
            raise ValueError(f"Error: specified IP address to block/unblock is not a valid IPv4 address: {ip}")

def script_handler(events, context):
    try:
        logging.info(f'block_ip.py called with event: {events}')
        # Inputs:
        ips_to_addrm_csv = events.ip_list
        block_list_ruleset_name = events.block_list_ruleset_name
        block_list_ssmparam_name = events.block_list_ssmparam_name
        waf_operation = events.waf_operation
        if waf_operation not in ["Block", "Unblock"]:
            raise ValueError(f"Error: specified WAF operation {waf_operation} is invalid")
        # Clean and validate user-provided list of IPs
        ips_to_addrm = [j.strip() for j in ips_to_addrm_csv.split(",")]
        validate_ipv4set(ips_to_addrm)

        # Get latest block IP set from SSM Param store
        logging.info(f'Updating WAF block IP list using BlockedIPs SSM Parameter')
        get_param_resp = ssm_client.get_parameter(
            Name=block_list_ssmparam_name,
        )
        block_list_ssmparam_val = get_param_resp['Parameter']['Value']
        logging.info(f'BlockedIPs SSM Parameter value before update: {block_list_ssmparam_val}')
        # Clean and validate all IPs in SSM Parameter block list
        address_list = [j.strip() for j in block_list_ssmparam_val.split(",")]
        validate_ipv4set(address_list)
        # Obtain new SSM Parameter value
        if waf_operation=="Block":
            logging.info(f"Blocking IPs: {', '.join(ips_to_addrm)}")
            address_list += ips_to_addrm
        elif waf_operation=="Unblock":
            logging.info(f"Unblocking IPs: {', '.join(ips_to_addrm)}")
            address_list = [j for j in address_list if j not in ips_to_addrm]
        # Dedupe and sort
        address_list = sorted(list(set(address_list)))
        # Set new SSM param value
        new_block_list_ssmparam_val = ",".join(address_list)
        block_list_resp = ssm_client.put_parameter(
            Name=block_list_ssmparam_name,
            Value=new_block_list_ssmparam_val,
            Overwrite=True
        )
        # Check new SSM param value
        time.sleep(3)
        get_param_resp2 = ssm_client.get_parameter(
            Name=block_list_ssmparam_name,
        )
        curval = get_param_resp2['Parameter']['Value']
        if curval != new_block_list_ssmparam_val:
            raise ValueError(f"Error: Current SSM Parameter value {curval} does not match expected value {new_block_list_ssmparam_val}")
        logging.info(f'BlockedIPs SSM Parameter value after change: {new_block_list_ssmparam_val}')

        # Update WAF
        cidrs_list = [z+"/32" for z in address_list]
        # Get the ipset identifier
        ipsets_list = waf_client.list_ip_sets(
            Scope='REGIONAL'
        )
        ipset_id = None
        for ipset in ipsets_list["IPSets"]:
            if ipset["Name"] == block_list_ruleset_name:
                ipset_id = ipset["Id"]
                break
        if ipset_id is None:
            raise Exception(f'Could not find ID for specified IPSet {block_list_ruleset_name}')
        logging.info(f'Found ID for IPSet {block_list_ruleset_name}: {ipset_id}')

        # Get the IPSet and lock token
        ip_set = waf_client.get_ip_set(
            Name=block_list_ruleset_name,
            Scope='REGIONAL',
            Id=ipset_id
        )
        address_list = ip_set['IPSet']['Addresses']
        lock_token = ip_set['LockToken']
        logging.info(f'Obtained a lock token for WAF block list set {block_list_ruleset_name}')
        logging.info(f'Updating WAF block list set {block_list_ruleset_name} with {len(cidrs_list)} CIDRs...')
        waf_client.update_ip_set(
            Name=block_list_ruleset_name,
            Scope='REGIONAL',
            Id=ipset_id,
            Addresses=cidrs_list,
            LockToken=lock_token
        )
        logging.info(f'Done updating WAF block list set {block_list_ruleset_name}')
        logging.info(f'The WAF block/unblock IP action has successfully completed!')
    except Exception as e:
        # We encountered a problem during the WAF update operation.
        # Log the exception, then re-raise it so lambda does not exit cleanly
        logging.exception(e)
        raise
