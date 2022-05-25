list_ip_sets_payload = {
    "NextMarker": "plinkthonk",
    "IPSets": [
        {
            "Name": "foobar",
            "Id": "00000000-0000-0000-0000-000000000000",
            "Description": "foobar ip list",
            "LockToken": "00000000-0000-0000-0000-000000000001",
            "ARN": "arn:aws:wafv2:us-east-1:000000000000:regional/ipset/foobar/00000000-0000-0000-0000-000000000000"
        },
        {
            "Name": "bazwuz",
            "Id": "11111111-0000-0000-0000-000000000000",
            "Description": "bazwuz ip list",
            "LockToken": "11111111-0000-0000-0000-000000000000",
            "ARN": "arn:aws:wafv2:us-east-1:000000000000:regional/ipset/bazwuz/11111111-0000-0000-0000-000000000000"
        }
    ]
}

get_ip_set_payload = {
    "IPSet": {
        "Name": "foobar",
        "Id": "00000000-0000-0000-0000-000000000000",
        "ARN": "arn:aws:wafv2:us-east-1:000000000000:regional/ipset/foobar/00000000-0000-0000-0000-000000000000",
        "Description": "IPs that should be blocked.",
        "IPAddressVersion": "IPV4",
        "Addresses": [
            "10.20.30.40/32",
            "10.20.30.41/32"
        ]
    },
    "LockToken": "00000000-0000-0000-0000-000000000001"
}

update_ip_set_payload = {
    "NextLockToken": "00000000-1111-2222-3333-000000000000"
}

get_parameter_payload_1 = {
    "Parameter": {
        "Name": "/DeploymentConfig/env/BlockedIPs",
        "Type": "String",
        "Value": "10.20.30.40,10.20.30.41",
        "Version": 1,
        "LastModifiedDate": "2000-01-01T00:00:00.000000-07:00",
        "ARN": "arn:aws:ssm:us-east-1:000000000000:parameter/DeploymentConfig/env/BlockedIPs",
        "DataType": "text"
    }
}

get_parameter_payload_2 = {
    "Parameter": {
        "Name": "/DeploymentConfig/env/BlockedIPs",
        "Type": "String",
        "Value": "1.2.3.4,10.20.30.40,10.20.30.41",
        "Version": 1,
        "LastModifiedDate": "2000-01-01T00:00:00.000000-07:00",
        "ARN": "arn:aws:ssm:us-east-1:000000000000:parameter/DeploymentConfig/env/BlockedIPs",
        "DataType": "text"
    }
}

put_parameter_payload = {
    "Version": 1,
    "Tier": "Standard"
}
