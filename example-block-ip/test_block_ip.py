import block_ip
from payloads import (
    list_ip_sets_payload,
    get_ip_set_payload,
    update_ip_set_payload,
    get_parameter_payload_1,
    get_parameter_payload_2,
    put_parameter_payload
)
import unittest
from unittest.mock import MagicMock, patch
import pytest
import collections

class TestBlockIp(unittest.TestCase):
    # Mock the AWS responses
    @patch.object(block_ip.waf_client, 'list_ip_sets', return_value=list_ip_sets_payload)
    @patch.object(block_ip.waf_client, 'get_ip_set', return_value=get_ip_set_payload)
    @patch.object(block_ip.waf_client, 'update_ip_set', return_value=update_ip_set_payload)
    @patch.object(block_ip.ssm_client, 'get_parameter', side_effect=[get_parameter_payload_1, get_parameter_payload_2])
    @patch.object(block_ip.ssm_client, 'put_parameter', return_value=put_parameter_payload)
    def test_block_ip(
        self, 
        mock_list_ip_sets, 
        mock_get_ip_set, 
        mock_update_ip_set,
        mock_get_param,
        mock_put_param
    ):
    
        # Assemble fake context
        context = {}

        # Make a fake Event type with same inputs as lambda event
        Event = collections.namedtuple(
            'Event', 
            [
                'ip_list', 
                'block_list_ruleset_name',
                'block_list_ssmparam_name',
                'waf_operation',
            ]
        )
    
        # A normal call that should go smoothly
        block_ip.script_handler(
            Event(
                ip_list="1.2.3.4",
                block_list_ruleset_name="foobar",
                block_list_ssmparam_name="/DeploymentConfig/env/BlockedIPs",
                waf_operation="Block"
            ),
            context
        )
    
        # Malformed IPs
        with self.assertRaises(ValueError):
            block_ip.script_handler(
                Event(
                    ip_list="0.1.2.356",
                    block_list_ruleset_name="foobar",
                    block_list_ssmparam_name="/DeploymentConfig/env/BlockedIPs",
                    waf_operation="Block"
                ),
                context
            )
    
            block_ip.script_handler(
                Event(
                    ip_list="192.168",
                    block_list_ruleset_name="foobar",
                    block_list_ssmparam_name="/DeploymentConfig/env/BlockedIPs",
                    waf_operation="Block"
                ),
                context
            )
    
            block_ip.script_handler(
                Event(
                    ip_list=(0x180+0x348),
                    block_list_ruleset_name="foobar",
                    block_list_ssmparam_name="/DeploymentConfig/env/BlockedIPs",
                    waf_operation="Block"
                ),
                context
            )

        # Invalid operation
        with self.assertRaises(ValueError):
            block_ip.script_handler(
                Event(
                    ip_list="1.2.3.4",
                    block_list_ruleset_name="foobar",
                    block_list_ssmparam_name="/DeploymentConfig/env/BlockedIPs",
                    waf_operation="Antidisestablishmentarianism"
                ),
                context
            )

if __name__=="__main__":
    unittest.main()
